
App
=======

The entire functionality has to be bundlet at one point. This is the `App` class.
The `App` class reads in the command line arguments, reads the configuration, 
creates the `ServiceProxy` objects, connects them with the `OidcHandler`, starts
the `cherrypy` instance and coordinates the application flow.


.. uml::
   :scale: 40 %

   !include docs/gen/classes.plantuml
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
   remove oidcproxy.base.App
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

argparse
--------

Our proxy should run on clients without a graphical user interface.
Therefore, every startup option must be given on the command line.
For command line arguments we use Python native module argparse (:cite:`argparse`). 
This way, users can display all recognized command line parameters with `--help`,
and the order of the command line arguments are not relevant.
We provide the following options:

  * `-c / --config-file` to specify the configuration file
  * `--print-sample-config` to print a default configuration
  * `--print-samle-ac` to print a default rule, policy and policy set
  * `--add-provider` in combination with `--client-id` and `--client-secret` to
    add a OpenID connect provider without dynamic registration
  * `-d / --daemonize` to start ARPOC as a daemon
  * `--check-ac` to do some checks on the defined access control entities.

CherryPy
--------

A reverse proxy is not different to a normal webserver in tasks like session
handling, listening on ports or parsing HTTP requests. The only difference is
that the objects it serves are not files or outputs of applications on the server
but the output of another webserver.
For all tasks of a normal HTTP server we use cherrypy (:cite:`cherrypy`).
Cherrypy is "a minimalist python web framework" (:cite:`cherrypy`).
To increase the security of our application, we run the webserver with reduced
privileges. We do this by using the `dropprivileges` plugin (:cite:`cherrypy_dropprivileges`).
Also the use case for our webserver is to run as a daemon. This is done with the
`daemonizer` plugin (:cite:`cherrypy_daemonizer`).
After parsing the requests the request must handled by the application.
The connector between CherryPy and the application is the dispatcher.
Based on the requested URL the dispatcher selects and calls a method of an object.
We used the `RoutesDispatcher` (:cite:`cherrypy_routes`) that selects the methods
based on matches with regular expressions.
For every service an instance of a `ServiceProxy` (todo: link) class is created,
likewise for special pages.
