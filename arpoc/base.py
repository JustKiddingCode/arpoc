# Python imports
import logging
import logging.config
import copy


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
from cherrypy.process.plugins import DropPrivileges, Daemonizer, PIDFile

from jinja2 import Environment, FileSystemLoader

from jwkest import jwt, BadSyntax

#### Own Imports

import arpoc.ac as ac
import arpoc.exceptions
import arpoc.config as config
import arpoc.cache
import arpoc.utils
from arpoc.plugins import EnvironmentDict, ObjectDict, ObligationsDict

#logging.basicConfig(level=logging.DEBUG)

LOGGING = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader(
    os.path.join(os.path.dirname(__file__), 'resources', 'templates')))

class OidcHandler:
    """ A class to handle the connection to OpenID Connect Providers """
    def __init__(self, cfg: config.OIDCProxyConfig):
        self.__oidc_provider: Dict[str, oic.oic.Client] = dict()
        self.cfg = cfg
        self._secrets: Dict[str, dict] = dict()
        self._cache = arpoc.cache.Cache()


#        assert self.cfg.proxy is not None

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
        registration_response: RegistrationResponse
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
                assert self.cfg.proxy is not None
                provider_info = client.provider_config(
                    provider['configuration_url'])
                redirect_uris = provider.redirect_uris if provider.redirect_uris else self.cfg.proxy[
                    'redirect_uris']
                args = {
                    "redirect_uris": redirect_uris,
                    "contacts": self.cfg.proxy['contacts']
                }
                registration_response = client.register(
                    provider_info["registration_endpoint"],
                    registration_token=provider['configuration_token'],
                    **args)
            else:
                raise arpoc.exceptions.OIDCProxyException(
                    "Error in the configuration file")
        except oic.exception.RegistrationError:
            LOGGING.warning("Provider %s returned an error on registration",
                            name)
            LOGGING.debug("Seems to be permament, so not retrying")
            return
        except (requests.exceptions.MissingSchema,
                requests.exceptions.InvalidSchema,
                requests.exceptions.InvalidURL):
            raise arpoc.exceptions.OIDCProxyException(
                "Error in the configuration file")

        self.__oidc_provider[name] = client
        self.__oidc_provider[name].redirect_uris = args["redirect_uris"]
        self._secrets[name] = registration_response.to_dict()

    def create_client_from_secrets(self, name: str,
                                   provider: config.ProviderConfig) -> None:
        """ Try to create an openid connect client from the secrets that are
            saved in the secrets file"""
        client_secrets = self._secrets[name]
        client = oic.oic.Client(client_authn_method=CLIENT_AUTHN_METHOD)
        client.provider_config(provider.configuration_url)
        client_reg = RegistrationResponse(**client_secrets)
        client.store_registration_info(client_reg)
        client.redirect_uris = client_secrets[
            'redirect_uris']
        self.__oidc_provider[name] = client
        self._secrets[name] = client_reg.to_dict()

    def get_userinfo_access_token(self, access_token: str) -> Tuple[int, Dict]:
        """ Get the user info if the user supplied an access token"""
        # TODO: error handling (no jwt)
        # TODO: allow issuer parameter in header here
        userinfo = {}
        LOGGING.debug(access_token)
        try:
            access_token_obj = jwt.JWT()
            access_token_obj.unpack(access_token)
            LOGGING.debug(access_token_obj.payload())
            issuer = access_token_obj.payload()['iss']
        except BadSyntax:
            LOGGING.debug("Decoding Access Token failed")
            if 'x-arpoc-issuer' in cherrypy.request.headers:
                LOGGING.debug("issuer hint found")
                issuer = cherrypy.request.headers['x-arpoc-issuer']
            else:
                raise Exception("400 - Bad Request") # TODO 

        # check if issuer is in provider list
        client = None
        for provider_name, obj in self.__oidc_provider.items():
            LOGGING.debug(obj)
            if obj.issuer == issuer:
                client = obj
                client_name = provider_name

        valid_until = 0
        if client:
            if self.cfg.openid_providers[client_name].do_token_introspection:
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
                        valid_until = arpoc.utils.now() + 30
            else:
                valid_until = arpoc.utils.now() + 30
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
            now = arpoc.utils.now()
            LOGGING.debug("refresh necessary: %s, now: %s",
                          cherrypy.session['refresh'], now)
            return cherrypy.session['refresh'] < now
        return False

    def need_claims(self, claims: List[str]) -> None:
        """ Maps claims to scopes and checks
            if the scopes were already requested.
            Else start auth procedure to get requested scopes"""
        cherrypy.session["url"] = cherrypy.url()
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
            raise cherrypy.HTTPRedirect(self.cfg.proxy.auth)

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
            valid_until, refresh_valid = self.get_validity_from_token(
                new_token)

            self._cache.put(
                hash_access_token, {
                    "state": state,
                    "valid_until": valid_until,
                    "userinfo": userinfo,
                    "scopes": new_token.scope
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

            self._cache.put(hash_access_token, {"userinfo": userinfo},
                            valid_until)

            return hash_access_token, userinfo

        # check if refresh is needed
        if 'hash_at' in cherrypy.session:
            hash_access_token = cherrypy.session['hash_at']
            now = arpoc.utils.now()
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

    def _get_oidc_client(self, name: str) -> oic.oic.Client:
        return self.__oidc_provider[name]

    @staticmethod
    def get_validity_from_token(token: oic.oic.Token) -> Tuple[int, int]:
        """Find the validity of the id_token, access_token and refresh_token """
        # how long is the information valid?
        # oauth has the expires_in (but only RECOMMENDED)
        # oidc has exp and iat required.
        # so if:  iat + expires_in < exp -> weird stuff (but standard compliant)
        (iat, exp) = (token.id_token['iat'], token.id_token['exp'])
        at_exp = exp
        try:
            at_exp = token.expires_in + iat
        except AttributeError:
            pass

        valid_until = min(at_exp, exp)
        refresh_valid = valid_until

        try:
            refresh_valid = arpoc.utils.now() + token.refresh_expires_in
        except AttributeError:
            try:
                if token.refresh_token:
                    refresh_valid = valid_until
                    # TODO: add token introspection for the refresh_token (if jwt)
            except AttributeError:
                # we don't have a refresh token
                pass

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
                                   code: str) -> oic.oic.Token:
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
        token = client.get_token(state=aresp["state"])

        assert isinstance(token, oic.oic.Token)
        return token

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

        # TODO: Here we should check that state has not been altered!

        token = self.get_access_token_from_code(kwargs['state'],
                                                kwargs['code'])

        hash_at = hashlib.sha256(str(token).encode()).hexdigest()
        cherrypy.session['hash_at'] = hash_at

        # check for scopes:
        response_check = self.check_scopes(cherrypy.session["scopes"],
                                           token.scope)
        if response_check:
            return response_check
        cherrypy.session["scopes"] = token.scope

        valid_until, refresh_valid = self.get_validity_from_token(token)
        userinfo = self.do_userinfo_request_with_state(state=kwargs["state"])
        self._cache.put(
            hash_at, {
                "state": kwargs['state'],
                "valid_until": valid_until,
                "userinfo": dict(userinfo),
                "scopes": token.scope
            }, refresh_valid)
        # There should be an url in the session so we can redirect
        if "url" in cherrypy.session:
            raise cherrypy.HTTPRedirect(cherrypy.session["url"])
        raise RuntimeError

    def _auth(self, scopes: Optional[Iterable[str]] = None) -> None:
        if not scopes:
            scopes = ["openid"]
        if "hash_at" in cherrypy.session:
            hash_at = cherrypy.session["hash_at"]
            try:
                scopes_set = set(scopes)
                scopes_set_session = set(self._cache[hash_at]["scopes"])

                if scopes_set.issubset(scopes_set_session):
                    return None
            except KeyError:
                pass

        if "state" in cherrypy.session:
            LOGGING.debug("state is already present")

        cherrypy.session["state"] = rndstr()
        cherrypy.session["nonce"] = rndstr()

        # we need to test the scopes later
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
                return tmpl.render(auth_page=self.cfg.proxy.auth,
                                   provider=provider)

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

    def _build_url(self, url: str, kwargs: Any) -> str:
        url = "{}/{}".format(self.cfg['origin_URL'], url)
        if kwargs:
            url = "{}?{}".format(url, urllib.parse.urlencode(kwargs))
        return url

    def _build_proxy_url(self, path: str = '', kwargs: Any = None) -> str:
        kwargs = {} if kwargs is None else kwargs
        this_url = "{}{}/{}".format(self._oidc_handler.cfg.proxy['baseuri'],
                                    self.cfg['proxy_URL'][1:], path)
        if kwargs:
            this_url = "{}?{}".format(this_url, urllib.parse.urlencode(kwargs))
        return this_url

    @staticmethod
    def _send_403(message: str = '') -> str:
        cherrypy.response.status = 403
        return "<h1>Forbidden</h1><br>%s" % message

    @staticmethod
    def build_access_dict(query_dict: Optional[Dict] = None) -> Dict:
        """Creates the access dict for the evaluation context """
        query_dict = query_dict if query_dict is not None else {}
        method = cherrypy.request.method
        headers = copy.copy(cherrypy.request.headers)
        headers.pop('host', None)
        headers.pop('Content-Length', None)
        headers['connection'] = "close"

        # Read request body
        request_body = ""
        if cherrypy.request.method in cherrypy.request.methods_with_bodies:
            request_body = cherrypy.request.body.read()

        return {"method": method, "body": request_body, "headers": headers, "query_dict" : query_dict}

    @cherrypy.expose
    def index(self, *args: Any, **kwargs: Any) -> str:
        """
            Connects to the origin_URL of the proxied service.
            Important: If a request parameter "url" is in the REQUEST, it will
            override the path information.
            /serviceA/urlinformation?url=test will translate to:
            <ServiceA>/test
        """
        try:
            del kwargs['_']
        except KeyError:
            pass
        _, userinfo = self._oidc_handler.get_userinfo()
        #called_url = cherrypy.url(qs=cherrypy.request.query_string)
        called_url_wo_qs = cherrypy.url()

        path = called_url_wo_qs[len(self._build_proxy_url()):]
        #LOGGING.debug("Called url was %s ", called_url)
        target_url = self._build_url(path, kwargs)

        object_dict = ObjectDict(objsetter=self.cfg['objectsetters'],
                                 initialdata={
                                     "path": path,
                                     "target_url": target_url,
                                     "service": self.service_name,
                                 })
        access = self.build_access_dict(query_dict=kwargs)
        context = {
            "subject": userinfo,
            "object": object_dict,
            "environment": EnvironmentDict(),
            "access": access
        }
        LOGGING.debug("Container is %s", self.ac)
        evaluation_result = self.ac.evaluate_by_entity_id(
            self.cfg['AC'], context)
        (effect, missing,
         obligations) = (evaluation_result.results[self.cfg['AC']],
                         evaluation_result.missing_attr,
                         evaluation_result.obligations)
        LOGGING.debug("Obligations are: %s", obligations)
        obligations_dict = ObligationsDict()
        obligations_result = obligations_dict.run_all(obligations, effect,
                                                      context,
                                                      self.cfg.obligations)

        if effect == ac.Effects.GRANT and all(obligations_result):
            return self._proxy(target_url, access)
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
    """ Dispatcher for cherrypy to force TLS """
    def __init__(self, tls_url: str, next_dispatcher: Dispatcher):
        super().__init__()
        self._tls_url = tls_url
        self._next_dispatcher = next_dispatcher

    def __call__(self, path_info: str) -> Dispatcher:
        if cherrypy.request.scheme == 'https':
            return self._next_dispatcher(path_info)
        return self._next_dispatcher(self._tls_url + path_info)
