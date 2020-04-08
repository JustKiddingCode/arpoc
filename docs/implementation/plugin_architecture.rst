.. _implementation_plugin:

Plugin Architecture
===================

.. uml::
   :scale: 40 %

   !include overview.plantuml
   
   hide oidcprovider
   hide user
   hide acentities
   hide object

Access control rules must be tailored to fit the individual needs.
Therefore we used a modular design, so that users can modify the behaviour to their needs.
As above figure illustrates, there are three possibilities to use plugins:

* Obligations
* Environment setters
* Object Setters

For each type the plugin must inherit from a specific class and the Python
module must be placed in specific configurable folder.

.. uml::
   :scale: 40 %

   !include gen/classes.plantuml
   remove arpoc.App
   remove arpoc.ac.Policy
   remove arpoc.ac.Policy_Set
   remove arpoc.ac.AC_Entity
   remove arpoc.ac.Rule
   remove arpoc.ac.common.Effects
   remove arpoc.ac.AC_Container
   remove arpoc.ac.EvaluationResult
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

Obligations
-----------

An obligation plugin gets the result of the access control evaluation and the
context data and must return a boolean.
If a single obligation does not return `True` then access is denied.
The obligation class must set the class attribute `name` and can referenced
by it from the access control entities.

In some businesses traceability is a big concern. These businesses can use
our log obligations.
We include the following obligations: log every access (`obl_log`), log only successful
accesses (`obl_log_successful`), log denied accesses (`obl_log_failed`).
Since we use the Python Logging module (:cite:`logging`), the loggers can perform various tasks,
from writing to a file on a local disk, writing to the system log, to writing a
mail. The default configuration of the logger can either be used without changes, with changes
like a changed filename, or completely changed.

Environment setters
-------------------

Environment setters are run when the evaluation process requests 
a specific environment attribute, referenced
by the class attribute `target`.
The return value of the environment setter is then used every time
the environment attribute is requested.

We include the following environment setters for time related attributes
(in parentheses the attribute key): time in "hh:mm:ss" format (`time`),
time and day in "YYYY-MM-DD HH:MM:SS" format (`datetime`), only hours as integers (`time_hour`), only minutes
as integer (`time_minute`), only seconds as integers (`time_second`). These 
environment setters do not use a timezone, i.e. they are given in UTC.

For an application example consider a company that wants to protect its employees for
overwork. This company can limit the time that a webservice is available via this
rule: `environment.time_hour >= 8 and environment.time_hour < 18`. This rule
would only evaluate to true between 08:00 and 17:59.

Object setters
--------------

Object setters are run when an object attribute is requested and not found.
Then, every enabled object setter is run in the order of their priority,
starting with the smallest priority.
Object setters are initialized with their configuration data and get the object
data as input.
One object setter can set as many attributes of the object as needed, though
object setters running later will override the values of previous ones.

We included two object setters: `urlmap` and `json`.

urlmap
^^^^^^^^^

The `urlmap` object setter takes a list of regular expressions and matches each
against the target path.
For example, if a service offers information about musicians and the url syntax
is `artist`/`album`/`title` the regex could be `(?P<artist>[\w ]+)/(?P<album>[\w ]+)/(?P<track>[\w ]+)`.
For the path `Rise Against/Appeal to Reason/Entertainment` the objectsetter
would set `Rise Against` as artist, `Appeal to Reason` as album and `Entertainment` as track.
Note that the regex must match the whole path, so a regex that sets a value only
based on the first folder, must end on something like `.*` to match.

json
^^^^^^^^^^

The `json` setter calls an URL, parses the results it gets as json, and adds the key
value pairs to the object data.
The json setter adds the the current object dictionary as request parameters.
For example, consider a read request from the Bell LaPadula Modell :cite:`belllapadula`.
A read request in the Bell La Padula modell is only possible if the subject's privilege level
is higher or equal to the object's privilege level.
The condition of a rule could look like: `subject.privilege >= object.privilege`.
To get the privilege of an object, the service provider can set up an endpoint
that maps the target path to the object's privilege. 
The endpoint can return a simple string as `{'privilege' : 5 }`.
In the configuration of our proxy
the user must enable the json object setter and enter the endpoint URL.
