import logging
import logging.config
import atexit
import warnings
import copy
import datetime

import argparse

import importlib.resources
import os, pwd, grp

from http.client import HTTPConnection

from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.oic.message import RegistrationResponse, AuthorizationResponse
from oic import rndstr
from oic.utils.http_util import Redirect

import urllib.parse

import yaml
import requests

import cherrypy
from cherrypy.process.plugins import DropPrivileges

import ac
from config import OIDCProxyConfig

from jwkest import jwt

logging.basicConfig(level=logging.DEBUG)

#HTTPConnection.debuglevel = 1

LOGGING = logging.getLogger()

with importlib.resources.path('resources', 'loggers.yml') as loggers_path, open(loggers_path) as ymlfile:
    LOG_CONF = yaml.safe_load(ymlfile)


class ServiceProxy:
    def __init__(self, service_name, oidc_handler):
        self.service_name = service_name
        self.cfg = cfg.services[self.service_name]
        self._oidc_handler = oidc_handler

    def _proxy(self, url):
        resp = requests.get(url)
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
        this_url = "{}{}/{}".format(cfg.proxy['hostname'],
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
            "subject": userinfo,
            "object": {
                "url": url,
                **kwargs
            },
            "environment": {}
        }

        proxy_url = self._build_url(url, **kwargs)
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings("ignore")
            warnings.filterwarnings(
                "always", category=ac.parser.SubjectAttributeMissingWarning)
            if ac.container.evaluate_by_entity_id(self.cfg['AC'],
                                                  context) == ac.Effects.GRANT:
                return self._proxy(proxy_url)
            else:
                if len(w) > 0:
                    # At least one SubjectAttributeMissingWarning was issued
                    # -> Are we logged in?
                    # set url in session to current attribute
                    if not userinfo:
                        cherrypy.session['url'] = self._build_proxy_url(
                            url, **kwargs)
                        raise cherrypy.HTTPRedirect("/auth")
                warn = "\n".join([str(warning.message) for warning in w])
                return self._send_403(warn)


class OidcHandler:
    def __init__(self):
        self.__oidc_provider = dict()

    def register_first_time(self,name,provider):
        client = Client(client_authn_method=CLIENT_AUTHN_METHOD)
        provider_info = client.provider_config(provider['configuration_url'])
        args = {
            "redirect_uris": cfg.proxy['redirect_uris'],
            "contacts": cfg.proxy['contacts']
        }
        registration_response = client.register(
            provider_info["registration_endpoint"],
            registration_token=provider['configuration_token'],
            **args)
        self.__oidc_provider[name] = client
        self.__oidc_provider[name].redirect_uris = args["redirect_uris"]
        return registration_response.to_dict()

    def create_client_from_secrets(self,name, provider, client_secrets):
        self.__oidc_provider[name] = Client(client_authn_method=CLIENT_AUTHN_METHOD)
        provider_info = self.__oidc_provider[name].provider_config(provider['configuration_url'])
        client_reg = RegistrationResponse(**client_secrets)
        self.__oidc_provider[name].store_registration_info(client_reg)
        self.__oidc_provider[name].redirect_uris = client_secrets['redirect_uris']

    def get_userinfo(self):
        """ Gets the userinfo from the OIDC Provider.
            This works in two steps:
                1. Check if the user supplied an Access Token
                2. Otherwise, check the session management if the user is logged in
        """
        if 'authorization' in cherrypy.request.headers:
            LOGGING.debug(cherrypy.request.headers['authorization'])
            if cherrypy.request.headers['authorization'].lower().startswith(
                    'bearer'):
                LOGGING.debug(cherrypy.request.headers['authorization'])
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
        qry = {key: kwargs[key] for key in ['state', 'session_state', 'code']}
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

        userinfo = client.do_user_info_request(state=aresp["state"])
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
            "scope": ["openid", "roles", "age", "groups"],
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
                auth_page = ""
                for key in self.__oidc_provider:
                    auth_page += "<a href='/auth/{}'>Login via {}</a><br/>".format(
                        key, key)
                return auth_page

        self._auth()

    def userinfo(self, **kwargs):
        return cherrypy.session['userinfo']

    def getRoutesDispatcher(self):
        d = cherrypy.dispatch.RoutesDispatcher()
        # Connect the Proxied Services
        for name, service in cfg.services.items():
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

        # Connect the Redirect URI
        LOGGING.debug(cfg.proxy['redirect'])
        d.connect('redirect',
                  cfg.proxy['redirect'],
                  controller=self,
                  action='redirect')
        d.connect('userinfo', '/userinfo', controller=self, action='userinfo')
        # Test auth required
        d.connect('auth', "/auth", controller=self, action='auth')
        d.connect('auth', "/auth/{name:.*?}", controller=self, action='auth')

        return d

def read_secrets():
    global secrets
    secrets_path = cfg.proxy['secrets']
    try:
        with open(secrets_path, 'r') as ymlfile:
            secrets = yaml.safe_load(ymlfile)
    except FileNotFoundError:
        secrets = dict()

    if not secrets:
        secrets = dict()



def save_secrets():
    global secrets
    secrets_path = cfg.proxy['secrets']
    with open(secrets_path, 'w') as ymlfile:
        yaml.safe_dump(secrets, ymlfile)


def run():
    parser = argparse.ArgumentParser(description='OIDC Proxy')
    parser.add_argument('-c', '--config-file')
    parser.add_argument('--print-sample-config',action='store_true')

    args = parser.parse_args()
    print(args)

    global cfg
    cfg = OIDCProxyConfig(config_file=args.config_file)
    if args.print_sample_config:
        cfg.print_sample_config()
        return 
    # Create secrets dir and change ownership (perm)
    secrets_dir = os.path.dirname(cfg.proxy['secrets'])
    os.makedirs(secrets_dir, exist_ok=True)
    uid = pwd.getpwnam(cfg.proxy['username'])[2]
    gid = grp.getgrnam(cfg.proxy['groupname'])[2]
    stat_info = os.stat(secrets_dir)
    if stat_info.st_uid != uid or stat_info.st_gid != gid:
        os.chown(secrets_dir, uid, gid)

    read_secrets()
    atexit.register(save_secrets)

    clients = dict()
    app = OidcHandler()
    for name, provider in cfg.openid_providers.items():
        # check if the client is/was already registered
        try:
            app.create_client_from_secrets(name, provider, secrets[name])
        except KeyError:
            response = app.register_first_time(name,provider)
            secrets[name] = response

    global_conf = {
        'log.screen': False,
        'log.access_file': '',
        'log.error_file': '',
        'server.socket_host': cfg.proxy['address'],
        'server.socket_port': cfg.proxy['port'],
        'server.ssl_private_key': cfg.proxy['keyfile'],
        'server.ssl_certificate': cfg.proxy['certfile'],
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
    cherrypy.quickstart(None, '/', app_conf)

if __name__ == "__main__":
    run()
