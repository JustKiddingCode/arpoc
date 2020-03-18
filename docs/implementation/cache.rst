Cache
======

Our reverse proxy is supposed to run continously for multiple days or even multiple
months. Keeping track of all subject attributes would lead to huge memory consumption,
even when the data will never be touched again.
Therefore we use a cache system. In the cache every item gets inserted with their
maximum life period and gets deleted once this period is over.
We use hexadecimal representation of the SHA-256 hash of the access token as key
and store the user information and the OpenID Connect Provider.
The cache stores the data as `CacheItem` objects with a minimum heap structure,
i.e. the smallest `timestamp` is on first position.
The `expire` function removes every item from the cache once the `timestamp` is
smaller than the current timestamp, i.e. the CacheItem's lifetime period is over.

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
   remove oidcproxy.base.OidcHandler
   remove oidcproxy.base.TLSOnlyDispatcher
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

