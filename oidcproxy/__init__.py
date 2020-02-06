""" Main module of the OIDC Proxy """

# Python imports
import logging
import logging.config
import atexit
import warnings
import copy
import datetime

import argparse

# For scheduling auth & registration to providers
import sched
import threading
import time

import importlib.resources
import os
import pwd
import grp

import hashlib

import urllib.parse

from http.client import HTTPConnection
#HTTPConnection.debuglevel = 1
from dataclasses import dataclass, field
from typing import List, Dict, Union, Tuple, Callable, Iterable, Optional, Any

# side packages

##oic
import oic.oic
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.oic.message import RegistrationResponse, AuthorizationResponse

from oic import rndstr
from oic.utils.http_util import Redirect
import oic.extension.client

import oic.exception

import yaml
import requests

import cherrypy
from cherrypy._cpdispatch import Dispatcher
from cherrypy.process.plugins import DropPrivileges

from jinja2 import Environment, FileSystemLoader

from jwkest import jwt

#### Own Imports

import oidcproxy.ac as ac
import oidcproxy.config as config
import oidcproxy.pap
import oidcproxy.cache
from oidcproxy.plugins import EnvironmentDict, ObjectDict

logging.basicConfig(level=logging.DEBUG)

LOGGING = logging.getLogger()

env = Environment(loader=FileSystemLoader(
    os.path.join(os.path.dirname(__file__), 'resources', 'templates')))


class OidcHandler:
    """ A class to handle the connection to OpenID Connect Providers """
    def __init__(self, cfg: config.OIDCProxyConfig):
        self.__oidc_provider: Dict[str, oic.oic.Client] = dict()
        self.cfg = cfg
        self._secrets: Dict[str, dict] = dict()
        self._cache = oidcproxy.cache.Cache()

    def get_secrets(self) -> Dict[str, dict]:
        """ Returns the secrets (client_id, client_secret) of the OIDC Relying Partys"""
        return self._secrets

    def register_first_time(self, name: str,
                            provider: config.ProviderConfig) -> None:
        """ Registers a client or reads the configuration from the registration endpoint

            If registration_url is present in the configuration file, then it will try
            to read the configuration using the registration_token.

            If configuration_url is present in the configuration file, it will try to
            set the configuration using the registration endpoint dynamically
            received with the well-known location url (configuration_url)

        """
        client = oic.oic.Client(client_authn_method=CLIENT_AUTHN_METHOD)
        registration_response: Union[None, RegistrationResponse]
        try:
            if provider.registration_url and provider.registration_token:
                provider_info = client.provider_config(
                    provider['configuration_url'])
                # Only read configuration
                registration_response = client.registration_read(
                    url=provider['registration_url'],
                    registration_access_token=provider['registration_token'])
                args = dict()
                args['redirect_uris'] = registration_response['redirect_uris']
            elif provider.configuration_url and provider.configuration_token:
                provider_info = client.provider_config(
                    provider['configuration_url'])
                args = {
                    "redirect_uris": self.cfg.proxy['redirect_uris'],
                    "contacts": self.cfg.proxy['contacts']
                }
                registration_response = client.register(
                    provider_info["registration_endpoint"],
                    registration_token=provider['configuration_token'],
                    **args)
            else:
                raise Exception("Error in the configuration file")
        except oic.exception.RegistrationError:
            LOGGING.debug("Provider %s returned an error on registration",
                          name)
            LOGGING.debug("Seems to be permament, so not retrying")
            return

        self.__oidc_provider[name] = client
        self.__oidc_provider[name].redirect_uris = args["redirect_uris"]
        self._secrets[name] = registration_response.to_dict()

    def create_client_from_secrets(self, name: str,
                                   provider: config.ProviderConfig,
                                   client_secrets: Dict) -> None:
        """ Try to create an openid connect client from the secrets that are
            saved in the secrets file"""
        self.__oidc_provider[name] = oic.oic.Client(
            client_authn_method=CLIENT_AUTHN_METHOD)
        self.__oidc_provider[name].provider_config(provider.configuration_url)
        client_reg = RegistrationResponse(**client_secrets)
        self.__oidc_provider[name].store_registration_info(client_reg)
        self.__oidc_provider[name].redirect_uris = client_secrets[
            'redirect_uris']
        self._secrets[name] = client_secrets

    def get_userinfo_access_token(self, access_token: str) -> Tuple[int, Dict]:
        """ Get the user info if the user supplied an access token"""
        userinfo = {}
        LOGGING.debug(access_token)
        access_token_obj = jwt.JWT()
        access_token_obj.unpack(access_token)
        LOGGING.debug(access_token_obj.payload())
        issuer = access_token_obj.payload()['iss']
        # check if issuer is in provider list
        client = None
        for _, obj in self.__oidc_provider.items():
            LOGGING.debug(obj)
            if obj.issuer == issuer:
                client = obj

        valid_until = 0
        if client:
            # do userinfo with provided AT
            # we need here the oauth extension client
            args = ["client_id", "client_authn_method", "keyjar", "config"]
            kwargs = {x: client.__getattribute__(x) for x in args}
            oauth_client = oic.extension.client.Client(**kwargs)
            for key, val in client.__dict__.items():
                if key.endswith("_endpoint"):
                    oauth_client.__setattr__(key, val)
            oauth_client.client_secret = client.client_secret
            introspection_res = oauth_client.do_token_introspection(
                request_args={
                    'token': access_token,
                    'state': rndstr()
                },
                authn_method='client_secret_basic')
            if introspection_res['active']:
                if 'exp' in introspection_res:
                    valid_until = introspection_res['exp']
                else:
                    valid_until = int(datetime.datetime.now().timestamp()) + 30
            userinfo = client.do_user_info_request(access_token=access_token)
        else:
            LOGGING.info(
                "Access token received, but no suitable provider in configuration"
            )
            LOGGING.info("Access token issuer %s", issuer)
        return valid_until, dict(userinfo)

    @staticmethod
    def _check_session_refresh() -> bool:
        """ checks if the session must be refreshed. If there is no session,
            then False is returned"""
        if 'refresh' in cherrypy.session:
            now = int(datetime.datetime.now().timestamp())
            LOGGING.debug("refresh necessary: %s, now: %s",
                          cherrypy.session['refresh'], now)
            return cherrypy.session['refresh'] < now
        return False

    def need_claims(self, claims: List[str]) -> None:
        """ Maps claims to scopes and checks
            if the scopes were already requested.
            Else start auth procedure to get requested scopes"""
        if 'provider' in cherrypy.session:
            provider = cherrypy.session['provider']
            scopes = set(["openid"])
            for claim in claims:
                LOGGING.debug("Need claim %s", claim)
                scopes |= set(
                    self.cfg.openid_providers[provider].claim2scope[claim])
            LOGGING.debug("Need scopes %s", scopes)
            self._auth(scopes)
        else:
            cherrypy.session["url"] = cherrypy.url()
            raise cherrypy.HTTPRedirect("/auth")

    @staticmethod
    def get_access_token_from_headers() -> Union[None, str]:
        """ Returns the Access Token from the authorization header.
            Strips the bearer part """
        if 'authorization' in cherrypy.request.headers:
            auth_header = cherrypy.request.headers['authorization']
            len_bearer = len("bearer")
            if len(auth_header) > len_bearer:
                auth_header_start = auth_header[0:len_bearer]

                if auth_header_start.lower() == 'bearer':
                    access_token = auth_header[len_bearer + 1:]
                    return access_token

        return None

    def refresh_access_token(self, hash_access_token: str) -> Tuple[str, Dict]:
        """ Refreshes the access token.
            This can only be done, if we are Client (normal web interface). """
        client = self._get_oidc_client(cherrypy.session['provider'])
        cache_entry = self._cache[hash_access_token]
        state = cache_entry['state']
        try:
            del self._cache[hash_access_token]

            userinfo = dict(client.do_user_info_request(state=state))
            new_token = client.get_token(state=state)
            LOGGING.debug("New token: %s", new_token)

            hash_access_token = hashlib.sha256(
                str(new_token.access_token).encode()).hexdigest()
            cherrypy.session['hash_at'] = hash_access_token
            valid_until = int(datetime.datetime.now().timestamp()) + 30

            if 'expires_in' in new_token.keys():
                valid_until = int(
                    datetime.datetime.now().timestamp()) + new_token.expires_in

            if "refresh_expires_in" in new_token.keys():
                refresh_valid = datetime.datetime.now().timestamp(
                ) + new_token.refresh_expires_in
            elif "refresh_token" in new_token.keys():
                raise NotImplementedError
            else:
                refresh_valid = valid_until

            self._cache.put(
                hash_access_token, {
                    "state": state,
                    "valid_until": valid_until,
                    "userinfo": userinfo,
                    "evaluation_cache": {}
                }, refresh_valid)
            return hash_access_token, userinfo
        except Exception as excep:
            LOGGING.debug(excep.__class__)
            raise

    def get_userinfo(self) -> Tuple[Optional[str], Dict]:
        """ Gets the userinfo from the OIDC Provider.
            This works in two steps:
                1. Check if the user supplied an Access Token
                2. Otherwise, check the session management if the user is logged in
        """
        access_token_header = self.get_access_token_from_headers()
        if access_token_header:
            hash_access_token = hashlib.sha256(
                access_token_header.encode()).hexdigest()
            try:
                return hash_access_token, self._cache[hash_access_token][
                    'userinfo']
            except KeyError:
                pass
            # how long is the token valid?

            valid_until, userinfo = self.get_userinfo_access_token(
                access_token_header)

            self._cache.put(hash_access_token, {
                "userinfo": userinfo,
                "evaluation_cache": {}
            }, valid_until)

            return hash_access_token, userinfo

        # check if refresh is needed
        if 'hash_at' in cherrypy.session:
            hash_access_token = cherrypy.session['hash_at']
            now = datetime.datetime.now().timestamp()
            # is the access token still valid?
            try:
                cache_entry = self._cache[hash_access_token]
            except KeyError:
                # hash_at is not in cache!
                LOGGING.debug('Hash at not in cache!')
                LOGGING.debug("Cache %s", self._cache.keys())
                return (None, {})

            # the entry valid_until is the validity of the refresh token, not of the cache entry
            if cache_entry['valid_until'] > now:
                return hash_access_token, cache_entry['userinfo']
            return self.refresh_access_token(hash_access_token)
        return None, {}


#                raise cherrypy.HTTPRedirect("/auth")

    def _get_oidc_client(self, name: str) -> oic.oic.Client:
        return self.__oidc_provider[name]

    @staticmethod
    def get_validity_from_resp(resp: oic.oic.AuthorizationResponse
                               ) -> Tuple[int, int]:
        """Find the validity of the id_token, access_token and refresh_token """
        # how long is the information valid?
        # oauth has the expires_in (but only RECOMMENDED)
        # oidc has exp and iat required.
        # so if:  iat + expires_in < exp -> weird stuff (but standard compliant)
        (iat, exp) = (resp['id_token']['iat'], resp['id_token']['exp'])
        at_exp = exp
        if "expires_in" in resp and resp["expires_in"]:
            at_exp = resp["expires_in"] + iat

        valid_until = min(at_exp, exp)

        if "refresh_expires_in" in resp:
            refresh_valid = datetime.datetime.now().timestamp(
            ) + resp['refresh_expires_in']
        elif "refresh_token" in resp:
            raise NotImplementedError
        else:
            refresh_valid = valid_until

        return (valid_until, refresh_valid)

    def do_userinfo_request_with_state(self, state: str) -> Dict:
        """ Perform the userinfo request with given state """
        client = self._get_oidc_client(cherrypy.session['provider'])
        try:
            userinfo = client.do_user_info_request(state=state)
        except oic.exception.CommunicationError as excep:
            exception_args = excep.args
            LOGGING.debug(exception_args)
            if exception_args[
                    0] == "Server responded with HTTP Error Code 405":
                # allowed methods in [1]
                if exception_args[1][0] in ["GET", "POST"]:
                    userinfo = client.do_user_info_request(
                        state=state, method=exception_args[1][0])
                else:
                    raise
        except oic.exception.RequestError as excep:
            LOGGING.debug(excep.args)
            raise
        return userinfo

    def get_access_token_from_code(self, state: str,
                                   code: str) -> oic.oic.AccessTokenResponse:
        """ Takes the OIDC Authorization Code,
            Performs the Access Token Request

            Returns: The Access Token Request Response"""
        # Get Access Token
        qry = {'state': state, 'code': code}
        client = self._get_oidc_client(cherrypy.session['provider'])
        aresp = client.parse_response(AuthorizationResponse,
                                      info=qry,
                                      sformat="dict")
        if state != aresp['state']:
            raise RuntimeError
        LOGGING.debug("Authorization Response %s",
                      dict(aresp))  # just code and state
        args = {"code": aresp["code"]}
        resp = client.do_access_token_request(
            state=aresp["state"],
            request_args=args,
            authn_method="client_secret_basic")
        LOGGING.debug("Access Token Request %s", resp)

        return resp

    @staticmethod
    def check_scopes(request: List, response: List) -> Optional[str]:
        """ Checks the request and response scopes
            and alert if the response scopes are not enough"""
        requested_scopes = set(request)
        response_scopes = set(response)
        # Did we get the requested scopes?
        if not requested_scopes.issubset(response_scopes):
            tmpl = env.get_template('500.html')
            info = {
                "error":
                "The openid provider did not respond with the requested scopes",
                "requested scopes": request,
                "scopes in answer": response
            }
            return tmpl.render(info=info)
        return None

    def redirect(self, **kwargs: Any) -> str:
        """Handler for the redirect method (entrypoint after forwarding to OIDC Provider """
        # We are trying to get the user info here from the provider
        LOGGING.debug(cherrypy.session)
        LOGGING.debug('kwargs is %s', kwargs)
        # Errors?
        if 'error' in kwargs:
            tmpl = env.get_template('500.html')
            return tmpl.render(info=kwargs)

        resp = self.get_access_token_from_code(kwargs['state'], kwargs['code'])

        hash_at = hashlib.sha256(str(resp).encode()).hexdigest()
        cherrypy.session['hash_at'] = hash_at

        # check for scopes:
        response_check = self.check_scopes(cherrypy.session["scopes"],
                                           resp["scope"])
        if response_check:
            return response_check
        cherrypy.session["scopes"] = resp['scope']

        valid_until, refresh_valid = self.get_validity_from_resp(resp)
        userinfo = self.do_userinfo_request_with_state(state=kwargs["state"])
        self._cache.put(
            hash_at, {
                "state": kwargs['state'],
                "valid_until": valid_until,
                "userinfo": dict(userinfo),
                "evaluation_cache": {}
            }, refresh_valid)
        # There should be an url in the session so we can redirect
        if "url" in cherrypy.session:
            raise cherrypy.HTTPRedirect(cherrypy.session["url"])
        raise RuntimeError

    def _auth(self, scopes: Union[None, Iterable[str]] = None) -> None:
        if not scopes:
            scopes = ["openid"]
        if "scopes" in cherrypy.session:
            # do we have already the requested scopes?
            scopes_set = set(scopes)
            scopes_set_session = set(cherrypy.session["scopes"])
            if scopes_set.issubset(scopes_set_session):
                return None

        if "state" in cherrypy.session:
            LOGGING.debug("state is already present")

        cherrypy.session["state"] = rndstr()
        cherrypy.session["nonce"] = rndstr()

        cherrypy.session["scopes"] = list(scopes)
        client = self._get_oidc_client(cherrypy.session['provider'])
        args = {
            "client_id": client.client_id,
            "response_type": "code",
            "scope": cherrypy.session["scopes"],
            "nonce": cherrypy.session["nonce"],
            "redirect_uri": client.redirect_uris[0],
            "state": cherrypy.session['state']
        }
        auth_req = client.construct_AuthorizationRequest(request_args=args)
        login_url = auth_req.request(client.authorization_endpoint)

        raise cherrypy.HTTPRedirect(login_url)

    def auth(self, **kwargs: Any) -> Optional[str]:
        """ Start an authentication request.
            Redirects to OIDC Provider if given"""
        # Do we have only one openid provider? -> use this
        if len(self.__oidc_provider) == 1:
            cherrypy.session['provider'] = self.__oidc_provider.keys(
            ).__iter__().__next__()
        else:
            if 'name' in kwargs and kwargs['name'] in self.__oidc_provider:
                cherrypy.session['provider'] = kwargs['name']
            else:
                LOGGING.debug(self.__oidc_provider)
                tmpl = env.get_template('auth.html')

                provider = dict()
                for key in self.__oidc_provider:
                    provider[key] = self.cfg.openid_providers[key][
                        'human_readable_name']
                return tmpl.render(auth_page='/auth', provider=provider)

        self._auth()
        return None  # we won't get here


class ServiceProxy:
    """ A class to perform the actual proxying """

    ac = ac.container

    def __init__(self, service_name: str, oidc_handler: OidcHandler,
                 cfg: config.ServiceConfig):
        self.service_name = service_name
        self.cfg = cfg
        self._oidc_handler = oidc_handler

    def _proxy(self, url: str, access: Dict) -> str:
        """ Actually perform the proxying.

            1. Setup request
            2. Setup authentication
            3. Get library method to use
            4. Perform outgoing request
            5. Answer the request
        """
        # Copy request headers
        access['headers'].pop('Authorization', None)

        # Setup authentication (bearer/cert)
        cert = None
        if self.cfg.authentication:
            # bearer?
            if self.cfg['authentication']['type'] == "Bearer":
                access['headers']['Authorization'] = "Bearer {}".format(
                    self.cfg['authentication']['token'])
            if self.cfg['authentication']['type'] == "Certificate":
                cert = (self.cfg['authentication']['certfile'],
                        self.cfg['authentication']['keyfile'])

        # Get requests method
        method_switcher: Dict[str, Callable] = {
            "GET": requests.get,
            "PUT": requests.put,
            "POST": requests.post,
            "DELETE": requests.delete
        }
        method = method_switcher.get(access['method'], None)
        if not method:
            raise NotImplementedError
        # Outgoing request
        kwargs = {"headers": access['headers'], "data": access['body']}
        if cert:
            kwargs['cert'] = cert
        resp = method(url, **kwargs)

        # Answer the request
        for header in resp.headers.items():
            if header[0].lower() == 'transfer-encoding':
                continue
            logging.debug("Proxy Request Header: %s", header)
            cherrypy.response.headers[header[0]] = header[1]
        cherrypy.response.status = resp.status_code
        return resp

    def _build_url(self, url: str, **kwargs: Any) -> str:
        url = "{}/{}".format(self.cfg['origin_URL'], url)
        if kwargs:
            url = "{}?{}".format(url, urllib.parse.urlencode(kwargs))
        return url

    def _build_proxy_url(self, url: str = '', **kwargs: Any) -> str:
        this_url = "{}{}/{}".format(self._oidc_handler.cfg.proxy['hostname'],
                                    self.cfg['proxy_URL'][1:], url)
        if kwargs:
            this_url = "{}?{}".format(this_url, urllib.parse.urlencode(kwargs))
        return this_url

    @staticmethod
    def _send_403(message: str = '') -> str:
        cherrypy.response.status = 403
        return "<h1>Forbidden</h1><br>%s" % message

    @staticmethod
    def build_access_dict() -> Dict:
        """Creates the access dict for the evaluation context """
        method = cherrypy.request.method
        headers = copy.copy(cherrypy.request.headers)
        headers.pop('host', None)
        headers.pop('Content-Length', None)
        headers['connection'] = "close"

        # Read request body
        request_body = ""
        if cherrypy.request.method in cherrypy.request.methods_with_bodies:
            request_body = cherrypy.request.body.read()

        return {"method": method, "body": request_body, "headers": headers}

    @cherrypy.expose
    def index(self, *args: Any, url: str = '', **kwargs: Any) -> str:
        """
            Connects to the origin_URL of the proxied service.
            Important: If a request parameter "url" is in the REQUEST, it will
            override the path information.
            /serviceA/urlinformation?url=test will translate to:
            <ServiceA>/test
        """
        LOGGING.debug("Incoming Request %s", url)
        LOGGING.debug("Kwargs are %s", kwargs)
        _, userinfo = self._oidc_handler.get_userinfo()

        object_dict = ObjectDict(objsetter=self.cfg['objectsetters'],
                                 initialdata={
                                     "url": url,
                                     **kwargs
                                 })
        access = self.build_access_dict()
        context = {
            "subject": userinfo,
            "object": object_dict,
            "environment": EnvironmentDict(),
            "access": access
        }

        proxy_url = self._build_url(url, **kwargs)
        evaluation_result = self.ac.evaluate_by_entity_id(
            self.cfg['AC'], context)
        (effect, missing) = (evaluation_result.results[self.cfg['AC']],
                             evaluation_result.missing_attr)
        if effect == ac.Effects.GRANT:
            return self._proxy(proxy_url, access)
        if len(missing) > 0:
            # -> Are we logged in?
            attr = set(missing)
            self._oidc_handler.need_claims(list(attr))
            warn = ("Failed to get the claims even we requested the " +
                    "right scopes.<br>Missing claims are:<br>")
            warn += "<br>".join(attr)
            return self._send_403(warn)
        return self._send_403("")


class TLSOnlyDispatcher(Dispatcher):
    def __init__(self, tls_url, next_dispatcher):
        self._tls_url = tls_url
        self._next_dispatcher = next_dispatcher

    def __call__(self, path_info):
        if cherrypy.request.scheme == 'https':
            return self._next_dispatcher(path_info)
        return self._next_dispatcher("/TLSRedirect" + path_info)


class App:
    """ Class for application handling.
        Reads configuration files,
        setups the oidc client classes
        and the dispatcher for the services"""
    def __init__(self) -> None:
        self._scheduler = sched.scheduler(time.time, time.sleep)
        self.thread = threading.Thread(target=self._scheduler.run)
        self.oidc_handler: OidcHandler
        self.config: config.OIDCProxyConfig

    @staticmethod
    def setup_loggers():
        """ Read the loggers configuration and configure the loggers"""
        with importlib.resources.path(
                'oidcproxy.resources',
                'loggers.yml') as loggers_path, open(loggers_path) as ymlfile:
            log_conf = yaml.safe_load(ymlfile)
        logging.config.dictConfig(log_conf)

    def retry(self,
              function: Callable,
              exceptions: Tuple,
              *args: Any,
              retries: int = 5,
              retry_delay: int = 30) -> None:
        """ Retries function <retries> times, as long as <exceptions> are thrown"""
        try:
            function(*args)
        except exceptions as excep:
            if retries > 0:
                LOGGING.debug(
                    "Retrying %s, parameters %s, failed with exception %s",
                    function, args,
                    type(excep).__name__)
                LOGGING.debug("Delaying for %s seconds", retry_delay)
                self._scheduler.enter(retry_delay,
                                      1,
                                      self.retry,
                                      (function, exceptions, *args),
                                      kwargs={
                                          'retries': retries - 1,
                                          'retry_delay': retry_delay
                                      })

    def tls_redirect(self, *args: Any, **kwargs: Any) -> None:
        url = cherrypy.url()
        raise cherrypy.HTTPRedirect(self.config.proxy['hostname'] +
                                    kwargs['url'])

    def get_routes_dispatcher(self) -> cherrypy.dispatch.RoutesDispatcher:
        """ Setups the Cherry Py dispatcher
            This connects makes the proxied services accessible"""
        dispatcher = cherrypy.dispatch.RoutesDispatcher()
        # Connect the Proxied Services
        for name, service_cfg in self.config.services.items():
            logging.debug(service_cfg)
            service_proxy_obj = ServiceProxy(name, self.oidc_handler,
                                             service_cfg)
            dispatcher.connect(name,
                               service_cfg['proxy_URL'],
                               controller=service_proxy_obj,
                               action='index')
            dispatcher.connect(name,
                               service_cfg['proxy_URL'] + "/{url:.*?}",
                               controller=service_proxy_obj,
                               action='index')
        pap = oidcproxy.pap.PolicyAdministrationPoint()
        dispatcher.connect('pap', "/pap", controller=pap, action='index')
        # Connect the Redirect URI
        LOGGING.debug(self.config.proxy['redirect'])
        for i in self.config.proxy['redirect']:
            dispatcher.connect('redirect',
                               i,
                               controller=self.oidc_handler,
                               action='redirect')
        dispatcher.connect('userinfo',
                           '/userinfo',
                           controller=self.oidc_handler,
                           action='userinfo')
        # Test auth required
        dispatcher.connect('auth',
                           "/auth",
                           controller=self.oidc_handler,
                           action='auth')
        dispatcher.connect('auth',
                           "/auth/{name:.*?}",
                           controller=self.oidc_handler,
                           action='auth')
        if self.config.proxy['https_only']:
            dispatcher.connect('TLSRedirect',
                               '/TLSRedirect/{url:.*?}',
                               controller=self,
                               action='tls_redirect')
            tls_dispatcher = TLSOnlyDispatcher(self.config.proxy['hostname'],
                                               dispatcher)
            return tls_dispatcher

        return dispatcher

    @staticmethod
    def read_secrets(filepath: str) -> Dict:
        """ Reads the secrets file from the filepath """
        try:
            with open(filepath, 'r') as ymlfile:
                secrets = yaml.safe_load(ymlfile)
        except FileNotFoundError:
            secrets = dict()

        return secrets

    def save_secrets(self) -> None:
        """ Saves the oidc rp secrets into the secrets file"""
        with open(self.config.proxy['secrets'], 'w') as ymlfile:
            yaml.safe_dump(self.oidc_handler.get_secrets(), ymlfile)

    def create_secrets_dir(self) -> None:
        assert isinstance(self.config.proxy, config.ProxyConfig)
        secrets_dir = os.path.dirname(self.config.proxy['secrets'])
        os.makedirs(secrets_dir, exist_ok=True)
        uid = pwd.getpwnam(self.config.proxy['username'])[2]
        gid = grp.getgrnam(self.config.proxy['groupname'])[2]

        for dirpath, _, filenames in os.walk(secrets_dir):
            os.chown(dirpath, uid, gid)
            for filename in filenames:
                os.chown(os.path.join(dirpath, filename), uid, gid)

    def setup_oidc_provider(self) -> None:
        """Setup the connection to all oidc providers in the config """
        assert isinstance(self.config, config.OIDCProxyConfig)
        self.oidc_handler = OidcHandler(self.config)

        #        atexit.register(app.save_secrets) TODO
        # Read secrets
        secrets = self.read_secrets(self.config.proxy['secrets'])

        for name, provider in self.config.openid_providers.items():
            # check if the client is/was already registered
            try:
                self.retry(self.oidc_handler.create_client_from_secrets,
                           (requests.exceptions.RequestException,
                            oic.exception.CommunicationError), name, provider,
                           secrets[name])
            except KeyError:
                self.retry(self.oidc_handler.register_first_time,
                           (requests.exceptions.RequestException,
                            oic.exception.CommunicationError), name, provider)
        self.thread.start()

    def run(self) -> None:
        """ Starts the application """
        #### Command Line Argument Parsing
        parser = argparse.ArgumentParser(description='OIDC Proxy')
        parser.add_argument('-c', '--config-file')
        parser.add_argument('--print-sample-config', action='store_true')
        parser.add_argument('--add-provider')
        parser.add_argument('--client-id')
        parser.add_argument('--client-secret')

        args = parser.parse_args()

        #### Read Configuration
        config.cfg = config.OIDCProxyConfig(config_file=args.config_file)
        if args.print_sample_config:
            config.cfg.print_sample_config()
            return

        self.config = config.cfg

        if args.add_provider and args.client_id and args.client_secret:
            # read secrets
            secrets = self.read_secrets(self.config.proxy['secrets'])

            # add secrets
            secret_dict = {
                "client_id": args.client_id,
                "client_secret": args.client_secret
            }
            secrets[args.add_provider] = secret_dict
            # save secrets
            with open(self.config.proxy['secrets'], 'w') as ymlfile:
                yaml.safe_dump(secrets, ymlfile)
            return

        #### Create secrets dir and change ownership (perm)
        self.create_secrets_dir()

        #### Setup OIDC Provider
        self.setup_oidc_provider()
        #### Setup Cherrypy
        global_conf = {
            'log.screen': False,
            'log.access_file': '',
            'log.error_file': '',
            'server.socket_host': config.cfg.proxy['address'],
            'server.socket_port': config.cfg.proxy['tls_port'],
            'server.ssl_private_key': config.cfg.proxy['keyfile'],
            'server.ssl_certificate': config.cfg.proxy['certfile'],
            'engine.autoreload.on': False
        }
        cherrypy.config.update(global_conf)
        app_conf = {
            '/': {
                'tools.sessions.on': True,
                'request.dispatch': self.get_routes_dispatcher()
            }
        }
        uid = pwd.getpwnam(self.config.proxy['username'])[2]
        gid = grp.getgrnam(self.config.proxy['groupname'])[2]
        DropPrivileges(cherrypy.engine, uid=uid, gid=gid).subscribe()

        #### Read AC Rules
        for acl_dir in self.config.access_control['json_dir']:
            ServiceProxy.ac.load_dir(acl_dir)

        #### Start Web Server
        cherrypy.tree.mount(None, '/', app_conf)
        if self.config.proxy['plain_port']:
            server2 = cherrypy._cpserver.Server()
            server2.socket_port = self.config.proxy['plain_port']
            server2._socket_host = "0.0.0.0"
            server2.thread_pool = 30
            server2.subscribe()

        cherrypy.engine.start()
        cherrypy.engine.block()
        self.thread.join()

    #    cherrypy.quickstart(None, '/', app_conf)
