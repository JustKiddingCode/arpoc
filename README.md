# ARPOC

A simple reverse proxy that adds OpenID Connect Authentication and lets you
write access rules for services you want to protect.

## Fast tutorial

You will need:

* A domain name `<domain>`
* A tls keypair (`<fullchain>`, `<privkey>`)
* A server with python (3.7 or newer) `<python3>`

### Install

* Download the repository and run `<python3> setup.py install`
* If successful you should now have the `oidcproxy` command.
* Make yourself familiar with the basic interface with `oidcproxy --help`.
* Create a configuration file `oidcproxy --print-sample-config`
* Save the configuration file (preferable under /etc/oidc-proxy/config.yml)
* Create a default access control hierarchy using `oidcproxy --print-sample-config`
* Save the access control hierarchy in a json file (defaultdir: /etc/oidc-proxy/acl/)

### Edit the sample configuration

Fill in the right values for `<keyfile>`, `<certfile>`, `<domainname>`, `<redirect>`
urls (path the openid connect providers will redirect the user to, with a leading
slash) and the contacts field (at least on valid mail adress).


### Add an openid connect provider

You need the configuration url (should end with .well-known/openid/configuration, cut this part of, it is added automatically).
You also need either:

* A configuration token
* A registration url and a registration token
* Client ID and Client Secret


#### Configuration URL and Token:

Choose a key under which oidcproxy will internally use for the provider.

Add both parameters to the config.yml under
`openid_providers -> <key> -> configuration_url`
`openid_providers -> <key> -> configuration_token`

#### Registration URL and registration token:

If you already registered your client and have a registration token add 
the configuration url, the registration url and the registration token
under to the config.yml file under
`openid_providers -> <key>` using the `configuration_url`, `registration_url`
and `registration_token`.

#### Client ID and Client Secret

Add the configuration url to the config.yml.
Call `oidcproxy --add-provider <key> --client-id <client_id> --client-secret <client-secret>`


### Add a service you want to protect.

You need the origin url, the proxy url and the key of an access control policy
set (the key of an ac entity in the json file with type policy set).

Choose a key which oidcproxy will internally use for the service.
Add the origin url and the proxy url (the path under which the service will be
available with a leading slash) using the `origin_URL` and `proxy_url` keys
under `services -> <service key> -> ` to the config.yml

*Now you should be able to access the service.*


## Dependencies

* [pyjwkest](https://github.com/IdentityPython/pyjwkest/) -- a python library for web tokens
* [lark-parser](https://github.com/lark-parser/lark) -- a parser for the access control language
* [pyoidc](https://github.com/OpenIDC/pyoidc) -- a python library for Open ID Connect
* ...
