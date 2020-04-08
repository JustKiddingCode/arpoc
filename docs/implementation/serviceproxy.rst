.. _implementation_serviceproxy:

ServiceProxy
============

The task of a `ServiceProxy`  object is to proxy a specific service.
In the initialisation of an object, the configuration of the service is given
to the object as well as an instance of the `OidcHandler` class. 
The configuration must contain an URL and the string of an policy set.
Through the CherryPy dispatcher the proxy URL gets connected to the `ServiceProxy`'s
`index` method.
The `index` method first builds the access control context, evaluates the policy
set, runs the obligations and then, if the policy set evaluated to `GRANT` and
all obligations returned `true` it gathers the object and delivers it.
Else an error message with the HTTP status code 403 (`Forbidden`) is returned.

.. uml::
   :scale: 40 %

   !include gen/classes.plantuml
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
   remove arpoc.base.OidcHandler
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

requests
--------

In the object delivery phase, we need to request the object from a different web
server, copy the response header and data and transmit the object to the requesting
users. This would require building a HTTP request, including encoding characters
to comply standars, opening a connection to the web server, and parsing the
response.
Furthermore, we would need to implement TLS certificate checks.
All these tasks are performed by the requests library (:cite:`requests`).
