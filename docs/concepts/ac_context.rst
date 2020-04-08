Attribut Retrieval
======================

.. uml::
   :scale: 40 %

   !include overview.plantuml

   hide user
   hide object
   hide obligations
   hide acentities


Our access control decisions are based on attributes. We provide a reverse
proxy with Attribute Based Access Control (ABAC).
This section describes how these attributes are gathered and the different
kinds of attributes. We call the set of all attributes access control context.

Definition Access Control Context
  We call the mapping from `subject`, `object`, `environment` and `access` to
  their respective mapping from key to value Access Control Context (AC Context).
  We call the key of a value in one of the four mappings `attribute key`.

.. _concepts_attribute_retrival_subject:

Subject
*******

The subject dictionary is filled with attributes or - as they are called in the
OpenID Connect Context -  `claims`.
The contents of the subject dictionary and the information from the OpenID Connect
Userinfo Endpoint are the same.
The scopes are requested on-demand. If an access control rule tries to access
a not existing claim, this claim is saved and - if the evaluation was not
successful (`GRANT`) - the scopes providing the missing claims
are requested from the userinfo endpoint.
For self-defined scopes the user can provide a mapping from claim to scope.

Object
*******

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
   remove arpoc.plugins.EnvironmentDict
   remove arpoc.plugins.ObligationsDict
   remove arpoc.plugins.PrioritizedItem
   remove arpoc.plugins._lib.EnvironmentAttribute
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



The object dictionary is initialized with the following keys:

* `path`: The requested path excluding the proxy path ( `/serviceA/foo` -> `/foo` )
* `target_url`: The url that is proxied, if access is granted
* `service`: The service name configured by arpoc configuration


The rest of the object dictionary is populated using so-called `objectsetters`.
The `objectsetters` can be implemented and activated using the configuration
file with the plugin system. 
All object setters are run when the first ac entities requests a
key that is not in the dictionary.

Each service can define the order the objectsetters are run.
In the initalization step, every subclass of the class ObjectSetter is collected
and added to a priority queue, with the priority specified in the service
configuration.

.. uml::
   :scale: 40%

   start
   
   while (objectsetter <- subclasses of ObjectSetter)
     if (objectsetter.name in activated objectsetters of service) then
       :add to priority queue;
     endif
   endwhile
   
   stop

Then, if the transformer requests a specific key, it is checked if the key is
already in the data. If the key is not in the dictionary, the object setters are run.
Each objectsetter receives the complete object dictionary as input and can modify
every attribute. Objectsetters that run later get the modified content from
object setters before.

.. uml::
   :scale: 40%

   start
   
   if (key in data) then (yes)
     : return data[key];
     stop
   endif
   while (objectsetter <- self.PriorityQueue)
     : data = objectsetter.run(data);
   endwhile
   if (key in data) then (yes)
     :return data[key];
     stop
   endif
   : raise KeyError;
   stop

Environment
***********

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
   remove arpoc.plugins.ObjectDict
   remove arpoc.plugins.ObligationsDict
   remove arpoc.plugins.PrioritizedItem
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

The environment variables are also populated with plugins. In contrast to the
objectsetters, each environment plugin specifies the attribute key it sets
(`target` attribut) and the plugin is only called when this attribute is requested.

.. uml::
   :scale: 40%

   start
   
   while (env_attr <- subclasses of EnvironmentAttribute)
     : add mapping from env_attr.target to env_attr;
   endwhile
   
   stop

.. uml::
   :scale: 40%

   start
   
   if (key in data) then (yes)
     : return data[key];
     stop
   endif
   if (key in mapping) then (yes)
     : data[key] = mapping[key].eval();
     : return data[key];
     stop
   endif
   : raise KeyError;
   stop

The value of the plugin is cached, so repeated requests of the same variable will
return the same value.

Access
******

The access dictionary is populated with the HTTP headers, the body (if present)
and HTTP method from the current HTTP request.
The following keys are present:

* `method`: The HTTP method (GET,POST,PUT,DELETE,PATCH)
* `body`: The request body
* `headers`: The request headers
* `query_dict`: The parsed query string (everything after the first '?' in the URL) in dictionary form.

