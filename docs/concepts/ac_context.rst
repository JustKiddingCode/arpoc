Attribut Retrieval
======================

.. uml::
   :scale: 40 %

   !incl
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


The object dictionary is initialized with the following keys:

* `path`: The requested path excluding the proxy path ( `/serviceA/foo` -> `/foo` )
* `target_url`: The url that is proxied, if access is granted
* `service`: The service name configured by oidcproxy configuration


The rest of the object dictionary is populated using so-called `objectsetters`.
The objectsetters can be freely implemented and activated using the configuration
file. All object setters are run when the first ac entities requests a 
key that is not in the dictionary.

Each service can influence the order when an objectsetter is run.
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

The environment variables are also populated with plugins. In contrast to the
objectsetters, each environment plugin specifies the attribute it shows and
the plugin is only called when this attribute is requested.
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

