.. _implementation_plugin:

Plugin Architecture
===================

.. uml::
   :scale: 40 %

   !include docs/overview.plantuml
   
   hide oidcprovider
   hide user
   hide acentities
   hide object

We used a modular design, so that users can modify the behaviour to their needs.
As above figure illustrates, there are three possibilities to use plugins:

* Obligations
* Environment setters
* Object Setters

For each type the plugin must inherit from a specific class and the python
module must be placed in specific configurable folder.

.. uml::
   :scale: 40 %

   !include docs/gen/classes.plantuml
   remove oidcproxy.App
   remove oidcproxy.ac.Policy
   remove oidcproxy.ac.Policy_Set
   remove oidcproxy.ac.AC_Entity
   remove oidcproxy.ac.Rule
   remove oidcproxy.ac.common.Effects
   remove oidcproxy.ac.AC_Container
   remove oidcproxy.ac.EvaluationResult
   remove oidcproxy.ac.conflict_resolution.AnyOfAny
   remove oidcproxy.ac.conflict_resolution.And
   remove oidcproxy.ac.conflict_resolution.ConflictResolution
   remove oidcproxy.ac.lark_adapter.CombinedTransformer
   remove oidcproxy.ac.lark_adapter.MyTransformer
   remove oidcproxy.ac.parser.BinaryNumeralOperator
   remove oidcproxy.ac.parser.BinaryOperator
   remove oidcproxy.ac.parser.BinaryOperatorAnd
   remove oidcproxy.ac.parser.BinaryOperatorIn
   remove oidcproxy.ac.parser.BinaryOperatorOr
   remove oidcproxy.ac.parser.BinarySameTypeOperator
   remove oidcproxy.ac.parser.BinaryStringOperator
   remove oidcproxy.ac.parser.Equal
   remove oidcproxy.ac.parser.ExistsTransformer
   remove oidcproxy.ac.parser.Greater
   remove oidcproxy.ac.parser.Lesser
   remove oidcproxy.ac.parser.MiddleLevelTransformer
   remove oidcproxy.ac.parser.NotEqual
   remove oidcproxy.ac.parser.OperatorTransformer
   remove oidcproxy.ac.parser.TopLevelTransformer
   remove oidcproxy.ac.parser.TransformAttr
   remove oidcproxy.ac.parser.UOP
   remove oidcproxy.ac.parser.matches
   remove oidcproxy.ac.parser.startswith
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

Obligations
-----------

An obligation plugin gets the result of the access control evaluation and the
context data and must return a boolean.
If an obligation does not return `True` then access is denied.
The obligation class must set the class attribute `name` and can referenced
by it from the access control entities.

Included obligations are:

* TODO
* TODO

Environment setters
-------------------

Environment setters are run when the evaluation process requests 
a specific environment attribute, referenced
by the class attribute `target`.
The return value of the environment setter is then used every time
the environment attribute is requested.

Included environment setters are:

* TODO
* TODO

Object setters
--------------

Object setters are run when an object attribute is requested and not found.
Then, every enabled object setter is run in the order of their priority,
starting with the smallest priority.
Object setters are initialized with their configuration data and get the object
data as input.
One object setter can set as many attributes of the object as needed, though
object setters running later will override the values of previous ones.

Included object setters are:

* TODO
* TODO
