Configuration
=============

Many parts of our proxy need configuration. The proxy component needs
configuration for the adress, the port and TLS key files.
Each service must specify the path where the service will be available and
the URL the service is available. Furthermore it needs to specify the policy
set which defines to verify if the access should be granted or denied.
For every OpenID Connect Provider at least a configuration URL must be supplied.
For the policy information point, the directory where the files with the
AC entities must be specified.
Some miscellaneous configuration, for example the logging level or paths of the
log file can also be made.
The complete configuration is encapsulated in the `OIDCProxyConfig` class.

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
   remove arpoc.ac.common.Effects
   remove arpoc.ac.conflict_resolution.AnyOfAny
   remove arpoc.ac.conflict_resolution.And
   remove arpoc.ac.conflict_resolution.ConflictResolution
   remove arpoc.ac.lark_adapter.CombinedTransformer
   remove arpoc.ac.lark_adapter.MyTransformer
   remove arpoc.ac.parser.BinaryNumeralOperator
   remove arpoc.ac.parser.BinaryOperator
   remove arpoc.ac.parser.BinaryOperatorAnd
   remove arpoc.ac.parser.BinaryOperatorIn
   remove arpoc.ac.parser.BinaryOperatorOr
   remove arpoc.ac.parser.BinarySameTypeOperator
   remove arpoc.ac.parser.BinaryStringOperator
   remove arpoc.ac.parser.Equal
   remove arpoc.ac.parser.ExistsTransformer
   remove arpoc.ac.parser.Greater
   remove arpoc.ac.parser.Lesser
   remove arpoc.ac.parser.MiddleLevelTransformer
   remove arpoc.ac.parser.NotEqual
   remove arpoc.ac.parser.OperatorTransformer
   remove arpoc.ac.parser.TopLevelTransformer
   remove arpoc.ac.parser.TransformAttr
   remove arpoc.ac.parser.UOP
   remove arpoc.ac.parser.matches
   remove arpoc.ac.parser.startswith
   remove arpoc.base.OidcHandler
   remove arpoc.base.ServiceProxy
   remove arpoc.base.TLSOnlyDispatcher
   remove arpoc.cache.Cache
   remove arpoc.cache.CacheItem
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

pyyaml
------

We want to make the configuration as easy as possible. Therefore, our configuration
file is in YAML (todo: ref) syntax. To parse the configuration file, we use
pyyaml (:cite:`pyyaml`). PyYAML parses the configuration into a dictionary which
we use in our `config` module.
