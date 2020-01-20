""" Main module of the OIDC Proxy """

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
import os, pwd, grp

from http.client import HTTPConnection
#HTTPConnection.debuglevel = 1

from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.oic.message import RegistrationResponse, AuthorizationResponse
from oic import rndstr
from oic.utils.http_util import Redirect

import oic.exception

import urllib.parse

import yaml
import requests

import cherrypy
from cherrypy.process.plugins import DropPrivileges

from jinja2 import Environment, FileSystemLoader

from jwkest import jwt

from dataclasses import dataclass, field
from typing import List

#### Own Imports

import oidcproxy.ac as ac
import oidcproxy.config as config
from oidcproxy.plugins import EnvironmentDict, ObjectDict

logging.basicConfig(level=logging.DEBUG)

LOGGING = logging.getLogger()

with importlib.resources.path(
        'oidcproxy.resources',
        'loggers.yml') as loggers_path, open(loggers_path) as ymlfile:
    LOG_CONF = yaml.safe_load(ymlfile)

env = Environment(loader=FileSystemLoader(
    os.path.join(os.path.dirname(__file__), 'resources', 'templates')))


@dataclass
class PAPNode:
    ID: str
    node_type: str
    resolver: str
    target: str
    effect: str
    condition: str
    policy_sets: List[object]
    policies: List[object]
    rules: List[object]


def create_PAPNode_Rule(rule: ac.Rule):
    return PAPNode(rule.entity_id, "rule", "", rule.target, rule.effect,
                   rule.condition, None, None, None)


def create_PAPNode_Policy(policy: ac.Policy):
    rules = [
        create_PAPNode_Rule(ServiceProxy.ac.rules[x]) for x in policy.rules
    ]
    return PAPNode(policy.entity_id, "policy", policy.conflict_resolution,
                   policy.target, "", "", None, None, rules)


def create_PAPNode_Policy_Set(policy_set: ac.Policy_Set):
    policies = [
        create_PAPNode_Policy(ServiceProxy.ac.policies[x])
        for x in policy_set.policies
    ]
    policy_sets = [
        create_PAPNode_Policy_Set(ServiceProxy.ac.policy_set[x])
        for x in policy_set.policy_sets
    ]
    return PAPNode(policy_set.entity_id, "policy set",
                   policy_set.conflict_resolution, policy_set.target, "", "",
                   policy_sets, policies, None)


class PolicyAdministrationPoint:
    def __init__(self):
        pass

    def index(self):
        tmpl = env.get_template('pap.html')
        s = []
        for ps in ServiceProxy.ac.policy_sets:
            s.append(create_PAPNode_Policy_Set(
                ServiceProxy.ac.policy_sets[ps]))

        return tmpl.render(pap_nodes=s)


class ServiceProxy:
    """ A class to perform the actual proxying """

    ac = ac.AC_Container()

    def __init__(self, service_name, oidc_handler):
        self.service_name = service_name
        self.cfg = oidc_handler.cfg.services[self.service_name]
        self._oidc_handler = oidc_handler

    def _proxy(self, url):
        """ Actually perform the proxying. 

            1. Setup request
               a) Copy request headers
               b) Copy request body
            2. Setup authentication
            3. Get library method to use
            4. Perform outgoing request
            5. Answer the request
        """
        # Copy request headers
        request_headers = copy.copy(cherrypy.request.headers)
        request_headers.pop('host', None)
        request_headers.pop('Authorization', None)
        request_headers.pop('Content-Length', None)
        request_headers['connection'] = "close"
        LOGGING.debug(request_headers)

        # Read request body
        request_body = ""
        if cherrypy.request.method in cherrypy.request.methods_with_bodies:
            request_body = cherrypy.request.body.read()

        # Setup authentication (bearer/cert)
        cert = None
        if 'Authentication' in self.cfg:
            # bearer?
            if self.cfg['Authentication']['type'] == "Bearer":
                request_headers['Authorization'] = "Bearer {}".format(
                    self.cfg['Authentication']['token'])
            if self.cfg['Authentication']['type'] == "Certificate":
                cert = (self.cfg['Authentication']['certfile'],
                        self.cfg['Authentication']['keyfile'])

        # Get requests method
        LOGGING.debug(cherrypy.request.method)
        method_switcher = {
            "GET": requests.get,
            "PUT": requests.put,
            "POST": requests.post,
            "DELETE": requests.delete
        }
        method = method_switcher.get(cherrypy.request.method, None)
        if not method:
            raise NotImplementedError

        # Outgoing request
        if cert:
            resp = method(url,
                          headers=request_headers,
                          data=request_body,
                          cert=cert)
        else:
            resp = method(url, headers=request_headers, data=request_body)

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
        context = {
            "subject":
            userinfo,
            "object":
            ObjectDict(service_name=self.service_name,
                       initialdata={
                           "url": url,
                           **kwargs
                       }),
            "environment":
            EnvironmentDict()
        }

        proxy_url = self._build_url(url, **kwargs)
        # TODO: Rewrite this?
        # We use own dictionaries for Object and Environment and override
        # the setter. We could do this here and ask for authentication, maybe
        # with an exception.
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings("ignore")
            warnings.filterwarnings(
                "always", category=ac.parser.SubjectAttributeMissingWarning)
            if self.ac.evaluate_by_entity_id(self.cfg['AC'],
                                             context) == ac.Effects.GRANT:
                return self._proxy(proxy_url)
            else:
                if len(w) > 0:
                    # At least one SubjectAttributeMissingWarning was issued
                    # -> Are we logged in?
                    # set url in session to current attribute
                    if not userinfo:
                        cherrypy.session["url"] = cherrypy.url()
                        #                        cherrypy.session['url'] = self._build_proxy_url(
                        #                            url, **kwargs)
                        raise cherrypy.HTTPRedirect("/auth")
                warn = "\n".join([str(warning.message) for warning in w])
                return self._send_403(warn)


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
        try:
            self.register_first_time(name, provider)
        except (requests.exceptions.RequestException,
                oic.exception.CommunicationError) as e:
            if retries > 0:
                LOGGING.debug("While retrying another exception occured %s",
                              type(e).__name__)
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
                oic.exception.CommunicationError) as e:
            if retries > 0:
                LOGGING.debug("While retrying another exception occured %s",
                              type(e).__name__)
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
        client_secrets = self._secrets[name]
        self.__oidc_provider[name] = Client(
            client_authn_method=CLIENT_AUTHN_METHOD)
        provider_info = self.__oidc_provider[name].provider_config(
            provider.configuration_url)
        client_reg = RegistrationResponse(**client_secrets)
        self.__oidc_provider[name].store_registration_info(client_reg)
        self.__oidc_provider[name].redirect_uris = client_secrets[
            'redirect_uris']

    def get_userinfo(self):
        """ Gets the userinfo from the OIDC Provider.
            This works in two steps:
                1. Check if the user supplied an Access Token
                2. Otherwise, check the session management if the user is logged in
        """
        if 'authorization' in cherrypy.request.headers:
            if cherrypy.request.headers['authorization'].lower().startswith(
                    'bearer'):
                access_token = cherrypy.request.headers['authorization'][len(
                    'bearer '):]
                LOGGING.debug(access_token)
                access_token_obj = jwt.JWT()
                access_token_obj.unpack(access_token)
                LOGGING.debug(access_token_obj.payload())
                issuer = access_token_obj.payload()['iss']
                # check if issuer is in provider list
                for key, obj in self.__oidc_provider.items():
                    LOGGING.debug(obj)
                    if obj.issuer == issuer:
                        client = obj
                # do userinfo with provided AT
                userinfo = client.do_user_info_request(
                    access_token=access_token)
                LOGGING.debug(userinfo)
                return userinfo

        # check if refresh is needed
        if 'refresh' in cherrypy.session and cherrypy.session['refresh'] < int(
                datetime.datetime.now().timestamp()):
            LOGGING.debug("get userinfo, refresh necessary: %s, now: %s",
                          cherrypy.session['refresh'],
                          int(datetime.datetime.now().timestamp()))
            LOGGING.debug("refreshing user information")
            # do a refresh
            client = cherrypy.session['client']
            state = cherrypy.session['state']
            # is requesting a new access token automatically
            try:
                cherrypy.session['userinfo'] = dict(
                    client.do_user_info_request(state=state))
                at = client.get_token(state=state)
                cherrypy.session['refresh'] = int(
                    datetime.datetime.now().timestamp()) + at.expires_in
            except TokenError:
                raise cherrypy.HTTPRedirect("/auth")

            LOGGING.debug(at)
        else:
            LOGGING.debug("using cached user information")

        return cherrypy.session.get('userinfo', {})

    def redirect(self, **kwargs):
        LOGGING.debug(cherrypy.session)
        #        qry = {key: kwargs[key] for key in ['state', 'session_state', 'code']}
        qry = {key: kwargs[key] for key in ['state', 'code']}
        LOGGING.debug('kwargs is %s' % kwargs)
        client = cherrypy.session['client']
        aresp = client.parse_response(AuthorizationResponse,
                                      info=qry,
                                      sformat="dict")
        LOGGING.debug(dict(aresp))
        args = {"code": aresp["code"]}
        resp = client.do_access_token_request(
            state=aresp["state"],
            request_args=args,
            authn_method="client_secret_basic")
        LOGGING.debug(resp)
        # how long is the information valid?
        # oauth has the expires_in (but only RECOMMENDED)
        # oidc has exp and iat required.
        # so if:  iat + expires_in < exp -> weird stuff (but standard compliant)
        (iat, exp) = (resp['id_token']['iat'], resp['id_token']['exp'])
        at_exp = exp
        if "expires_in" in resp and resp["expires_in"]:
            at_exp = resp["expires_in"] + iat
        cherrypy.session['refresh'] = min(at_exp, exp)

        userinfo = client.do_user_info_request(state=aresp["state"],
                                               method="GET")
        cherrypy.session["userinfo"] = dict(userinfo)

        if "url" in cherrypy.session:
            raise cherrypy.HTTPRedirect(cherrypy.session["url"])

    def _auth(self):
        cherrypy.session["state"] = rndstr()
        cherrypy.session["nonce"] = rndstr()
        LOGGING.debug(cherrypy.session['client'].redirect_uris)
        args = {
            "client_id": cherrypy.session['client'].client_id,
            "response_type": "code",
            "scope": ["openid", "email", "profile"],
            "nonce": cherrypy.session["nonce"],
            "redirect_uri": cherrypy.session['client'].redirect_uris,
            "state": cherrypy.session['state']
        }
        auth_req = cherrypy.session['client'].construct_AuthorizationRequest(
            request_args=args)
        login_url = auth_req.request(
            cherrypy.session['client'].authorization_endpoint)
        raise cherrypy.HTTPRedirect(login_url)

    def auth(self, name='', **kwargs):
        # Do we have only one openid provider? -> use this
        if len(self.__oidc_provider) == 1:
            cherrypy.session['client'] = copy.copy(
                self.__oidc_provider.values().__iter__().__next__())
        else:
            if name and name in self.__oidc_provider:
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

    def getRoutesDispatcher(self):
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
        pap = PolicyAdministrationPoint()
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
                response = app.register_first_time(name, provider)
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
            'request.dispatch': app.getRoutesDispatcher()
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
