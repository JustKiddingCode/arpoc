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

   !include classes.plantuml
   remove arpoc.App
   remove arpoc.ac.Policy
   remove arpoc.ac.Policy_Set
   remove arpoc.ac.AC_Entity
   remove arpoc.ac.Rule
   remove arpoc.ac.AC_Container
   remove arpoc.ac.EvaluationResult
   remove arpoc.ac.conflict_resolution.AnyOfAny
   remove arpoc.ac.conflict_resolution.And
   remove arpoc.ac.conflict_resolution.ConflictResolution
   remove arpoc.ac.common.Effects
   remove arpoc.ac.parser.TransformAttr
   remove arpoc.ac.parser.TopLevelTransformer
   remove arpoc.ac.parser.OperatorTransformer
   remove arpoc.ac.parser.MiddleLevelTransformer
   remove arpoc.ac.parser.ExistsTransformer
   remove arpoc.ac.lark_adapter.MyTransformer
   remove arpoc.ac.lark_adapter.CombinedTransformer
   remove arpoc.base.ServiceProxy
   remove arpoc.base.TLSOnlyDispatcher
   remove arpoc.cache.Cache
   remove arpoc.cache.CacheItem
   remove arpoc.config.ACConfig
   remove arpoc.config.Misc
   remove arpoc.config.OIDCProxyConfig
   remove arpoc.config.ProviderConfig
   remove arpoc.config.ProxyConfig
   remove arpoc.config.ServiceConfig
   remove arpoc.exceptions.ACEntityMissing
   remove arpoc.exceptions.AttributeMissing
   remove arpoc.exceptions.BadRuleSyntax
   remove arpoc.exceptions.BadSemantics
   remove arpoc.exceptions.ConfigError
   remove arpoc.exceptions.DuplicateKeyError
   remove arpoc.exceptions.EnvironmentAttributeMissing
   remove arpoc.exceptions.OIDCProxyException
   remove arpoc.exceptions.ObjectAttributeMissing
   remove arpoc.exceptions.SubjectAttributeMissing
   remove arpoc.pap.PAPNode
   remove arpoc.pap.PolicyAdministrationPoint
   remove arpoc.ac.parser.BinaryNumeralOperator
   remove arpoc.ac.parser.BinaryOperator
   remove arpoc.ac.parser.BinaryOperatorAnd
   remove arpoc.ac.parser.BinaryOperatorIn
   remove arpoc.ac.parser.BinaryOperatorOr
   remove arpoc.ac.parser.BinarySameTypeOperator
   remove arpoc.ac.parser.BinaryStringOperator
   remove arpoc.ac.parser.Equal
   remove arpoc.ac.parser.Greater
   remove arpoc.ac.parser.Lesser
   remove arpoc.ac.parser.NotEqual
   remove arpoc.ac.parser.UOP
   remove arpoc.ac.parser.matches
   remove arpoc.ac.parser.startswith
   remove arpoc.plugins.EnvironmentDict
   remove arpoc.plugins.ObjectDict
   remove arpoc.plugins.ObligationsDict
   remove arpoc.plugins.PrioritizedItem
   remove arpoc.plugins._lib.EnvironmentAttribute
   remove arpoc.plugins._lib.ObjectSetter
   remove arpoc.plugins._lib.Obligation
   remove arpoc.plugins.env_attr_time.EnvAttrDateTime
   remove arpoc.plugins.env_attr_time.EnvAttrTime
   remove arpoc.plugins.env_attr_time.EnvAttrTimeHour
   remove arpoc.plugins.env_attr_time.EnvAttrTimeMinute
   remove arpoc.plugins.env_attr_time.EnvAttrTimeSecond
   remove arpoc.plugins.obj_json.obj_json
   remove arpoc.plugins.obj_urlmap.ObjUrlmap
   remove arpoc.plugins.obl_loggers.Log
   remove arpoc.plugins.obl_loggers.LogFailed
   remove arpoc.plugins.obl_loggers.LogSuccessful
   remove arpoc.special_pages.Userinfo

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
