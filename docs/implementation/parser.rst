.. _implementation_plugin:

Parser
===================

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
   remove oidcproxy.base.OidcHandler
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

