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

import urllib.parse

from http.client import HTTPConnection
#HTTPConnection.debuglevel = 1
from dataclasses import dataclass, field
from typing import List

# side packages

##oic
from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.oic.message import RegistrationResponse, AuthorizationResponse
from oic import rndstr
from oic.utils.http_util import Redirect

import oic.exception

import yaml
import requests

import cherrypy
from cherrypy.process.plugins import DropPrivileges

from jinja2 import Environment, FileSystemLoader

from jwkest import jwt

#### Own Imports

import oidcproxy.ac as ac
import oidcproxy.config as config
import oidcproxy.pap
from oidcproxy.plugins import EnvironmentDict, ObjectDict

logging.basicConfig(level=logging.DEBUG)

LOGGING = logging.getLogger()

with importlib.resources.path(
        'oidcproxy.resources',
        'loggers.yml') as loggers_path, open(loggers_path) as ymlfile:
    LOG_CONF = yaml.safe_load(ymlfile)

env = Environment(loader=FileSystemLoader(
    os.path.join(os.path.dirname(__file__), 'resources', 'templates')))


class ServiceProxy:
    """ A class to perform the actual proxying """

    ac = ac.container

    def __init__(self, service_name, oidc_handler):
        self.service_name = service_name
        self.cfg = oidc_handler.cfg.services[self.service_name]
        self._oidc_handler = oidc_handler

    def _proxy(self, url, access):
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
        method_switcher = {
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
            logging.debug(header)
            cherrypy.response.headers[header[0]] = header[1]
        cherrypy.response.status = resp.status_code
        return resp

    def _build_url(self, url, **kwargs):
        url = "{}/{}".format(self.cfg['origin_URL'], url)
        if kwargs:
            url = "{}?{}".format(url, urllib.parse.urlencode(kwargs))
        return url

    def _build_proxy_url(self, url='', **kwargs):
        this_url = "{}{}/{}".format(self._oidc_handler.cfg.proxy['hostname'],
                                    self.cfg['proxy_URL'][1:], url)
        if kwargs:
            this_url = "{}?{}".format(this_url, urllib.parse.urlencode(kwargs))
        return this_url

    def _send_403(self, message=''):
        cherrypy.response.status = 403
        return "<h1>Forbidden</h1><br>%s" % message

    def build_access_dict(self):
        method = cherrypy.request.method
        headers = copy.copy(cherrypy.request.headers)
        headers.pop('host', None)
        headers.pop('Content-Length', None)
        headers['connection'] = "close"

        # Read request body
        body = ""
        if cherrypy.request.method in cherrypy.request.methods_with_bodies:
            request_body = cherrypy.request.body.read()

        return {"method": method, "body": body, "headers": headers}

    @cherrypy.expose
    def index(self, *args, url='', **kwargs):
        """
            Connects to the origin_URL of the proxied service.
            Important: If a request parameter "url" is in the REQUEST, it will
            override the path information.
            /serviceA/urlinformation?url=test will translate to:
            <ServiceA>/test
        """
        LOGGING.debug(url)
        LOGGING.debug(kwargs)
        userinfo = self._oidc_handler.get_userinfo()
        object_dict = ObjectDict(service_name=self.service_name,
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
        effect, missing = self.ac.evaluate_by_entity_id(
            self.cfg['AC'], context)
        if effect == ac.Effects.GRANT:
            return self._proxy(proxy_url, access)
        if len(missing) > 0:
            # -> Are we logged in?
            attr = set(missing)
            self._oidc_handler.need_claims(attr)
            warn = "Failed to get the claims even we requested the right scopes.<br>Missing claims are:<br>"
            warn += "<br>".join(attr)
            return self._send_403(warn)
        return self._send_403("")


class OidcHandler:
    """ A class to handle the connection to OpenID Connect Providers """
    def __init__(self, cfg):
        self.__oidc_provider = dict()
        self.cfg = cfg
        self.__secrets_file = None

    def register_first_time(self, name, provider):
        """ Registers a client or reads the configuration from the registration endpoint

            If registration_url is present in the configuration file, then it will try
            to read the configuration using the registration_token.

            If configuration_url is present in the configuration file, it will try to
            set the configuration using the registration endpoint dynamically
            received with the well-known location url (configuration_url)

        """
        client = Client(client_authn_method=CLIENT_AUTHN_METHOD)
        registration_response = None
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

    def retry_register_first_time(self, name, provider, scheduler, retries=5):
        """ Retry register_first_time function every 30 seconds <retries> times. """
        try:
            self.register_first_time(name, provider)
        except (requests.exceptions.RequestException,
                oic.exception.CommunicationError) as excep:
            if retries > 0:
                LOGGING.debug("While retrying another exception occured %s",
                              type(excep).__name__)
                LOGGING.debug("Connection to provider %s failed.",
                              provider['human_readable_name'])
                LOGGING.debug("Delaying client registration for 30 seconds")
                scheduler.enter(30, 1, self.retry_register_first_time,
                                (name, provider, scheduler, retries - 1))
            else:
                LOGGING.info(
                    "Connection to provider %s failed too many tries, will not retry",
                    provider['human_readable_name'])

    def retry_create_client_from_secrets(self,
                                         name,
                                         provider,
                                         scheduler,
                                         retries=5):
        """ Retries to register to an openid provider <provider> and schedule
            the task <retries> times if it fails using <scheduler>

            If successfull the provider will be added to self.__oidc_provider
            (in create_client_from_secrets)
        """
        try:
            self.create_client_from_secrets(name, provider)
        except (requests.exceptions.RequestException,
                oic.exception.CommunicationError) as excep:
            if retries > 0:
                LOGGING.debug("While retrying another exception occured %s",
                              type(excep).__name__)
                LOGGING.debug("Connection to provider %s failed.",
                              provider['human_readable_name'])
                LOGGING.debug("Delaying client registration for 30 seconds")
                scheduler.enter(30, 1, self.retry_create_client_from_secrets,
                                (name, provider, scheduler, retries - 1))
            else:
                LOGGING.info(
                    "Connection to provider %s failed too many tries, will not retry",
                    provider['human_readable_name'])

    def create_client_from_secrets(self, name, provider):
        """ Try to create an openid connect client from the secrets that are
            saved in the secrets file"""
        client_secrets = self._secrets[name]
        self.__oidc_provider[name] = Client(
            client_authn_method=CLIENT_AUTHN_METHOD)
        self.__oidc_provider[name].provider_config(provider.configuration_url)
        client_reg = RegistrationResponse(**client_secrets)
        self.__oidc_provider[name].store_registration_info(client_reg)
        self.__oidc_provider[name].redirect_uris = client_secrets[
            'redirect_uris']

    def get_userinfo_access_token(self, access_token):
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
        if client:
            # do userinfo with provided AT
            userinfo = client.do_user_info_request(access_token=access_token)
        return userinfo

    def _check_session_refresh(self):
        """ checks if the session must be refreshed. If there is no session,
            then False is returned"""
        if 'refresh' in cherrypy.session:
            now = int(datetime.datetime.now().timestamp())
            LOGGING.debug("refresh necessary: %s, now: %s",
                          cherrypy.session['refresh'], now)
            return cherrypy.session['refresh'] < now
        return False

    def need_claims(self, claims):
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

    def get_userinfo(self):
        """ Gets the userinfo from the OIDC Provider.
            This works in two steps:
                1. Check if the user supplied an Access Token
                2. Otherwise, check the session management if the user is logged in
        """
        if 'authorization' in cherrypy.request.headers:
            auth_header = cherrypy.request.headers['authorization'].lower()
            if auth_header.startswith('bearer'):
                access_token = auth_header[len('bearer '):]
                return self.get_userinfo_access_token(access_token)

        # check if refresh is needed
        if self._check_session_refresh():
            LOGGING.debug("refreshing user information")
            # do a refresh
            client = cherrypy.session['client']
            # TODO: shouldn't that be a new one?
            state = cherrypy.session['state']
            # is requesting a new access token automatically
            try:
                LOGGING.debug(client.grant)
                cherrypy.session['userinfo'] = dict(
                    client.do_user_info_request(state=state))
                access_token = client.get_token(state=state)
                cherrypy.session['refresh'] = int(datetime.datetime.now(
                ).timestamp()) + access_token.expires_in
                return cherrypy.session['userinfo']
            except Exception as e:
                LOGGING.debug(e.__class__)
                raise


#                raise cherrypy.HTTPRedirect("/auth")

        else:
            LOGGING.debug("using cached user information")
            return cherrypy.session.get('userinfo', {})

    def redirect(self, **kwargs):
        LOGGING.debug(cherrypy.session)
        LOGGING.debug('kwargs is %s' % kwargs)
        if 'error' in kwargs:
            tmpl = env.get_template('500.html')
            return tmpl.render(info=kwargs)
        #        qry = {key: kwargs[key] for key in ['state', 'session_state', 'code']}
        qry = {key: kwargs[key] for key in ['state', 'code']}
        client = cherrypy.session['client']
        aresp = client.parse_response(AuthorizationResponse,
                                      info=qry,
                                      sformat="dict")
        LOGGING.debug("Authorization Response %s",
                      dict(aresp))  # just code and state
        args = {"code": aresp["code"]}
        resp = client.do_access_token_request(
            state=aresp["state"],
            request_args=args,
            authn_method="client_secret_basic")
        LOGGING.debug("Access Token Request %s", resp)

        # check for scopes:
        requested_scopes = set(cherrypy.session["scopes"])
        response_scopes = set(resp['scope'])
        if not requested_scopes.issubset(response_scopes):
            tmpl = env.get_template('500.html')
            info = {
                "error":
                "The openid provider did not respond with the requested scopes",
                "requested scopes": cherrypy.session["scopes"],
                "scopes in answer": resp['scope']
            }
            return tmpl.render(info=info)
        cherrypy.session["scopes"] = resp['scope']
        cherrypy.session["state"] = aresp['state']

        # how long is the information valid?
        # oauth has the expires_in (but only RECOMMENDED)
        # oidc has exp and iat required.
        # so if:  iat + expires_in < exp -> weird stuff (but standard compliant)
        (iat, exp) = (resp['id_token']['iat'], resp['id_token']['exp'])
        at_exp = exp
        if "expires_in" in resp and resp["expires_in"]:
            at_exp = resp["expires_in"] + iat
        cherrypy.session['refresh'] = min(at_exp, exp)
        try:
            userinfo = client.do_user_info_request(state=aresp["state"])
        except oic.exception.RequestError as excep:
            LOGGING.debug(excep.args)
            raise

        cherrypy.session["userinfo"] = dict(userinfo)

        if "url" in cherrypy.session:
            raise cherrypy.HTTPRedirect(cherrypy.session["url"])

    def _auth(self, scopes=None):
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
        LOGGING.debug("Before redirect_uris %s",
                      cherrypy.session['client'].redirect_uris)
        args = {
            "client_id": cherrypy.session['client'].client_id,
            "response_type": "code",
            "scope": cherrypy.session["scopes"],
            "nonce": cherrypy.session["nonce"],
            "redirect_uri": cherrypy.session['client'].redirect_uris[0],
            "state": cherrypy.session['state']
        }
        auth_req = cherrypy.session['client'].construct_AuthorizationRequest(
            request_args=args)
        login_url = auth_req.request(
            cherrypy.session['client'].authorization_endpoint)
        LOGGING.debug("After redirect_uris %s",
                      cherrypy.session['client'].redirect_uris)

        raise cherrypy.HTTPRedirect(login_url)

    def auth(self, name='', **kwargs):
        # Do we have only one openid provider? -> use this
        if len(self.__oidc_provider) == 1:
            cherrypy.session['provider'] = self.__oidc_provider.keys(
            ).__iter__().__next__()
            cherrypy.session['client'] = copy.copy(
                self.__oidc_provider.values().__iter__().__next__())
        else:
            if name and name in self.__oidc_provider:
                cherrypy.session['provider'] = name
                cherrypy.session['client'] = copy.copy(
                    self.__oidc_provider[name])
            else:
                LOGGING.debug(self.__oidc_provider)
                tmpl = env.get_template('auth.html')

                provider = dict()
                for key in self.__oidc_provider:
                    provider[key] = self.cfg.openid_providers[key][
                        'human_readable_name']
                return tmpl.render(auth_page='/auth', provider=provider)

        self._auth()

    def userinfo(self, **kwargs):
        return cherrypy.session['userinfo']

    def get_routes_dispatcher(self):
        d = cherrypy.dispatch.RoutesDispatcher()
        # Connect the Proxied Services
        for name, service in self.cfg.services.items():
            logging.debug(service)
            service_proxy_obj = ServiceProxy(name, self)
            d.connect(name,
                      service['proxy_URL'],
                      controller=service_proxy_obj,
                      action='index')
            d.connect(name,
                      service['proxy_URL'] + "/{url:.*?}",
                      controller=service_proxy_obj,
                      action='index')
        pap = oidcproxy.pap.PolicyAdministrationPoint()
        d.connect('pap', "/pap", controller=pap, action='index')
        # Connect the Redirect URI
        LOGGING.debug(self.cfg.proxy['redirect'])
        for i in self.cfg.proxy['redirect']:
            d.connect('redirect', i, controller=self, action='redirect')
        d.connect('userinfo', '/userinfo', controller=self, action='userinfo')
        # Test auth required
        d.connect('auth', "/auth", controller=self, action='auth')
        d.connect('auth', "/auth/{name:.*?}", controller=self, action='auth')

        return d

    def read_secrets(self, filepath):
        self.secrets_file = filepath
        try:
            with open(self.secrets_file, 'r') as ymlfile:
                self._secrets = yaml.safe_load(ymlfile)
        except FileNotFoundError:
            self._secrets = dict()

        if not self._secrets:
            self._secrets = dict()

    def save_secrets(self):
        with open(self.secrets_file, 'w') as ymlfile:
            yaml.safe_dump(self._secrets, ymlfile)


def run():
    """ Starts the application """
    #### Command Line Argument Parsing
    parser = argparse.ArgumentParser(description='OIDC Proxy')
    parser.add_argument('-c', '--config-file')
    parser.add_argument('--print-sample-config', action='store_true')

    args = parser.parse_args()

    #### Read Configuration
    config.cfg = config.OIDCProxyConfig(config_file=args.config_file)
    if args.print_sample_config:
        cfg.print_sample_config()
        return
    #### Create secrets dir and change ownership (perm)
    secrets_dir = os.path.dirname(config.cfg.proxy['secrets'])
    os.makedirs(secrets_dir, exist_ok=True)
    uid = pwd.getpwnam(config.cfg.proxy['username'])[2]
    gid = grp.getgrnam(config.cfg.proxy['groupname'])[2]
    for dirpath, dirnames, filenames in os.walk(secrets_dir):
        os.chown(dirpath, uid, gid)
        for filename in filenames:
            os.chown(os.path.join(dirpath, filename), uid, gid)

    #### Setup OIDC Provider
    clients = dict()
    app = OidcHandler(config.cfg)

    app.read_secrets(config.cfg.proxy['secrets'])
    atexit.register(app.save_secrets)

    scheduler = sched.scheduler(time.time, time.sleep)
    for name, provider in config.cfg.openid_providers.items():
        # check if the client is/was already registered
        try:
            try:
                app.create_client_from_secrets(name, provider)
            except (requests.exceptions.RequestException,
                    oic.exception.CommunicationError):
                LOGGING.debug("Connection to provider %s failed.",
                              provider['human_readable_name'])
                LOGGING.debug("Delaying client registration for 30 seconds")
                scheduler.enter(30, 1, app.retry_create_client_from_secrets,
                                (name, provider, scheduler))
        except KeyError:
            try:
                app.register_first_time(name, provider)
            except (requests.exceptions.RequestException,
                    oic.exception.CommunicationError):
                LOGGING.debug("Connection to provider %s failed.",
                              provider['human_readable_name'])
                LOGGING.debug("Delaying client registration for 30 seconds")
                scheduler.enter(30, 1, app.retry_register_first_time,
                                (name, provider, scheduler))
    t = threading.Thread(target=scheduler.run)
    t.start()
    #### Setup Cherrypy
    global_conf = {
        'log.screen': False,
        'log.access_file': '',
        'log.error_file': '',
        'server.socket_host': config.cfg.proxy['address'],
        'server.socket_port': config.cfg.proxy['port'],
        'server.ssl_private_key': config.cfg.proxy['keyfile'],
        'server.ssl_certificate': config.cfg.proxy['certfile'],
        'engine.autoreload.on': False
    }
    cherrypy.config.update(global_conf)
    logging.config.dictConfig(LOG_CONF)
    app_conf = {
        '/': {
            'tools.sessions.on': True,
            'request.dispatch': app.get_routes_dispatcher()
        }
    }
    DropPrivileges(cherrypy.engine, uid=uid, gid=gid).subscribe()

    #### Read AC Rules
    for acl_dir in config.cfg.access_control['json_dir']:
        ServiceProxy.ac.load_dir(acl_dir)

    #### Start Web Server
    cherrypy.tree.mount(None, '/', app_conf)

    server2 = cherrypy._cpserver.Server()
    server2.socket_port = 80
    server2._socket_host = "0.0.0.0"
    server2.thread_pool = 30
    server2.subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()
    t.join()


#    cherrypy.quickstart(None, '/', app_conf)
