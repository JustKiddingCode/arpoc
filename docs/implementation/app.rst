
App
=======

The entire functionality has to be bundlet at one point. This is the `App` class.
The `App` class reads in the command line arguments, reads the configuration, 
creates the `ServiceProxy` objects, connects them with the `OidcHandler`, starts
the `cherrypy` instance and coordinates the application flow.


.. uml::
   :scale: 40 %

   !include docs/gen/classes.plantuml
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
   remove arpoc.base.OidcHandler
   remove arpoc.base.App
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
