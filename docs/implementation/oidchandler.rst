.. _implementation_oidchandler:

OidcHandler
============

The `OidcHandler` gets either called from a `ServiceProxy` instance or from
an `App` instance.

A `ServiceProxy` instance either wants subject attributes (`get_userinfo`)
or returns with an request for specific claims (`need_claims`). 
In the `get_userinfo` method it is checked if the user supplied an access token
via the HTTP request headers (command line usage) 
or if an access token is saved in the session of the user (webbrowser usage).
If an access token was found, the user information from the cache are returned.
If the cache does not contain information, then an empty dictionary is returned.
Note that here no authentication is enforced.
If the `need_claims` method was called, the evaluation process returned that
one or more specific subject attribute was missing to evaluate a rule.
These claims are then converted to a list of scopes.
These scopes are then asked for in the userinfo request if an access token was
was found, or the user gets redirected either to a list of OpenID connect providers
where he can choose his provider, or he gets redirected to the OpenID connect provider
if only one is supported.

The App instance calls the `OidcHandler` to setup the connection with the OpenID
Connect Providers. Either the client id and client secret were already found
(`create_client_from_secrets`) or the client (our proxy) must register
at the provider (`register_first_time`).

.. uml::
   :scale: 40 %

   !include docs/gen/classes.plantuml
   remove oidcproxy.App
   remove oidcproxy.ac.Policy
   remove oidcproxy.ac.Policy_Set
   remove oidcproxy.ac.AC_Entity
   remove oidcproxy.ac.Rule
   remove oidcproxy.ac.AC_Container
   remove oidcproxy.ac.EvaluationResult
   remove oidcproxy.ac.conflict_resolution.AnyOfAny
   remove oidcproxy.ac.conflict_resolution.And
   remove oidcproxy.ac.conflict_resolution.ConflictResolution
   remove oidcproxy.ac.common.Effects
   remove oidcproxy.ac.parser.TransformAttr
   remove oidcproxy.ac.parser.TopLevelTransformer
   remove oidcproxy.ac.parser.OperatorTransformer
   remove oidcproxy.ac.parser.MiddleLevelTransformer
   remove oidcproxy.ac.parser.ExistsTransformer
   remove oidcproxy.ac.lark_adapter.MyTransformer
   remove oidcproxy.ac.lark_adapter.CombinedTransformer
   remove oidcproxy.base.ServiceProxy
   remove oidcproxy.base.TLSOnlyDispatcher
   remove oidcproxy.cache.Cache
   remove oidcproxy.cache.CacheItem
   remove oidcproxy.config.ACConfig
   remove oidcproxy.config.Misc
   remove oidcproxy.config.OIDCProxyConfig
   remove oidcproxy.config.ProviderConfig
   remove oidcproxy.config.ProxyConfig
   remove oidcproxy.config.ServiceConfig
   remove oidcproxy.exceptions.ACEntityMissing
   remove oidcproxy.exceptions.AttributeMissing
   remove oidcproxy.exceptions.BadRuleSyntax
   remove oidcproxy.exceptions.BadSemantics
   remove oidcproxy.exceptions.ConfigError
   remove oidcproxy.exceptions.DuplicateKeyError
   remove oidcproxy.exceptions.EnvironmentAttributeMissing
   remove oidcproxy.exceptions.OIDCProxyException
   remove oidcproxy.exceptions.ObjectAttributeMissing
   remove oidcproxy.exceptions.SubjectAttributeMissing
   remove oidcproxy.pap.PAPNode
   remove oidcproxy.pap.PolicyAdministrationPoint
   remove oidcproxy.ac.parser.BinaryNumeralOperator
   remove oidcproxy.ac.parser.BinaryOperator
   remove oidcproxy.ac.parser.BinaryOperatorAnd
   remove oidcproxy.ac.parser.BinaryOperatorIn
   remove oidcproxy.ac.parser.BinaryOperatorOr
   remove oidcproxy.ac.parser.BinarySameTypeOperator
   remove oidcproxy.ac.parser.BinaryStringOperator
   remove oidcproxy.ac.parser.Equal
   remove oidcproxy.ac.parser.Greater
   remove oidcproxy.ac.parser.Lesser
   remove oidcproxy.ac.parser.NotEqual
   remove oidcproxy.ac.parser.UOP
   remove oidcproxy.ac.parser.matches
   remove oidcproxy.ac.parser.startswith
   remove oidcproxy.plugins.EnvironmentDict
   remove oidcproxy.plugins.ObjectDict
   remove oidcproxy.plugins.ObligationsDict
   remove oidcproxy.plugins.PrioritizedItem
   remove oidcproxy.plugins._lib.EnvironmentAttribute
   remove oidcproxy.plugins._lib.ObjectSetter
   remove oidcproxy.plugins._lib.Obligation
   remove oidcproxy.plugins.env_attr_time.EnvAttrDateTime
   remove oidcproxy.plugins.env_attr_time.EnvAttrTime
   remove oidcproxy.plugins.env_attr_time.EnvAttrTimeHour
   remove oidcproxy.plugins.env_attr_time.EnvAttrTimeMinute
   remove oidcproxy.plugins.env_attr_time.EnvAttrTimeSecond
   remove oidcproxy.plugins.obj_json.obj_json
   remove oidcproxy.plugins.obj_urlmap.ObjUrlmap
   remove oidcproxy.plugins.obl_loggers.Log
   remove oidcproxy.plugins.obl_loggers.LogFailed
   remove oidcproxy.plugins.obl_loggers.LogSuccessful
   remove oidcproxy.special_pages.Userinfo

pyoidc
---------------------

All subject attributes are claims of an OpenID Connect provider.
Therefore we need to communicate with OpenID Connect Provider, act as
a relying party and comply with the respective standards.
The library `pyoidc` (:cite:`pyoidc`) enables us to comply with the standard
without implementing it on our own.

pyjwkest
----------------------

If the user does a request with an access token included, we need to contact
the issuer of this access token to ensure that the access token is valid.
Because many issuers (TODO: cite/prove) use JWTs we can parse them and contact
the issuer that is stated inside the JWT.
`pyoidc` uses for this task the library `pyjwkest` (:cite:`pyjwkest`) 
which we use as well.
