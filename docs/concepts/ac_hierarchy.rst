************
AC Entities
************

.. uml::
   :scale: 40 %

   !include docs/overview.plantuml
   
   remove object
   remove user
   remove oidcprovider
   remove OIDC
   remove obligations
   remove objinf
   remove environment

AC Entities allow users to granularly specify which conditions have to be
met to allow or deny the access.
It follows the concepts of XACML, while focusing on increased readability and
easier creation. The user defines rules, policies or policy sets, which
in turn can define other objects like effects, obligations and conflict resolutions.
We first start with AC Effects, then explain the access control hierarchy focus
on conflict resolution and explain the evaluation process in depth.
Then we explain the access control language, i.e. the language conditions can
be specified in. The last element of ac entities are obligations and we
explain how obligations can be used to ensure
conditions are met after an access control decision.

Effects
========================

Effects define if the access should be granted (`GRANT`) or not (`DENY`).
Only rules define their effects directly, the effects of policies and policy
sets are determined with their conflict resolution.

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

Access Control Hierarchy
========================

.. uml::
   :scale: 40 %

   !include docs/gen/classes.plantuml
   remove oidcproxy.App
   remove oidcproxy.ac.AC_Container
   remove oidcproxy.ac.EvaluationResult
   remove oidcproxy.ac.common.Effects
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

We use three levels of access control entities.
The highest are policy sets, then policies and then rules.
Every entity (policy set, policy, rule) has an unique id, and a target.
In the evaluation process, an entity is only evaluated if the target is evaluated to true.
The id is used by other entities to link to each other.
Every entity can furthermore provide a description which is used merely for
display purpose.

Every policy set can contain other policy sets and/or policies.
Every policy can contain one or more rules.
Policies and policy sets specify a conflict resolution which is used to determine
the effect the policy has after the containing rules are evaluated.

Rules have a condition and an effect.

Conflict Resolution
===================

.. uml::
   :scale: 40 %

   !include docs/gen/classes.plantuml
   remove oidcproxy.App
   remove oidcproxy.ac.AC_Container
   remove oidcproxy.ac.AC_Entity
   remove oidcproxy.ac.EvaluationResult
   remove oidcproxy.ac.Policy
   remove oidcproxy.ac.Policy_Set
   remove oidcproxy.ac.Rule
   remove oidcproxy.ac.common.Effects
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

In the evaluation process of a policy or a policy set `A`,the conflict resolver
of `A` gets notified each time an ac entity contained in `A` finished its evaluation
process.
The conflict resolution is called with the entity id and the result of the evaluation.
It can then decide if the evaluation process must carry on or the result will not
change with other evaluation.

We use two conflict resolution algorithm: `ANY` and `AND`.

The `ANY` algorithm evaluates to `GRANT` as soon as any of the contained ac entities
evaluated to `GRANT`. After the first `GRANT` is transmitted to the conflict 
resolution, `check_break` will return `True` and `get_result` will return `GRANT`.
If none of the ac entity evaluated to `DENY` or `GRANT`, the conflict resolution
will return `None`. If no ac entity evaluated to `GRANT` but at least one entity
evaluated to `DENY`, `DENY` is returend.

The `AND` algorithm evalutes to `GRANT` only if at least one of the contained ac entities
evaluated to `GRANT` and every other entity evaluated to `GRANT` or  `None`. 
After the first `DENY` is transmitted to the conflict resolution, `check_break`
will return `True` and `get_result` returns `DENY`.


Evaluation Process
==================

The process of evaluation of a policy set A is as follows:

#. Check the target specifier, if False, abort
#. For every policy set B contained in A: evaluate policy set B.
#. For every policy P contained in A: evaluate policy P.
#. Let `Res` be the list of results of every policy set and every policy in A:
   Run the conflict resolution A specified with `Res` and get result for policy set A.

The process of evaluation of a policy P is as follows:

#. Check the target specifier. If False, abort
#. For every rule R contained in P: Evaluate R.
#. Let `Res` be the list of results of every rule R in P:
   Run the conflict resolution A specified with `Res` and get result for policy P.

The process of evaluation of a rule R is as follows:

#. Check the target specifier. If False, abort
#. Check condition specifier. If True return Effect, else return the inverse of Effect.


Improvements
------------

To increase speed, two mechanisms apply:
The resolver gets the result as soon as as a policy is evaluated.
The resolver can abort the evaluation process if the result is fixed.
This can be useful if, e.g. the access is denied, as soon as one rule denied
the access.

We describe the algorithm more formally with the next two sequence diagrams.
The first diagram shows the evaluation of a policy set, while the second pictures
the evaluation of a policy including more details of the evaluation of a rule.

.. uml::
   :scale: 60%

   caption Sequence diagram for policy set evaluation
   skinparam DiagramBorderThickness 2
   !include docs/concepts/seq_ps_evaluation.puml

.. uml::
   :scale: 60%

   caption Sequence diagram for policy evaluation
   skinparam DiagramBorderThickness 2
   !include docs/concepts/seq_p_evaluation.puml

Error Handling
^^^^^^^^^^^^^^^^^^

TODO: Move into Implementation chapter
In the evaluation of an ac entity two errors can occur: a missing AC entity or
missing attributes of the subject, object, environment or access.


Missing ac entities
"""""""""""""""""""

If an ac entity is missing, e.g. a typing error, a log message is generated
with the log level `Warning`.
The referencing entity evaluates to `None` in this case. Note that this is only
true if the missing entity type is called for evaluation, i.e. if the conflict
resolution algorithm already decided the result of the policy, a missing rule
will not change this result.

Missing attributes
""""""""""""""""""

If the evaluation tries to access an argument that is not provided by the corresponding
dictionary, an exception of one of the following types is raised:

* SubjectAttributeMissing
* ObjectAttributeMissing
* EnvironmentAttributeMissing
* AccessAttributeMissing

The evaluation process catches these exceptions sets his result to None
and if an subject attribute was missing, adds the key to a list.
After all AC entities are evaluated, the ac entity that started the evaluation
has a list of all subject attributes that are missing.

Access Control Language
=======================

To specify the conditions that have to be met for an access, we wanted a language
that was simple to read and write, give us the possibility to combine conditions,
support multiple comparisons of strings as well as integers
(equals, not equal, greater/lesser (or equal), string startswith, string matches regex).
It should also support complex datatypes, such as dictionaries and lists, next to
basic datatypes (integers and strings).
Because python is a widely known language,
the syntax should be easy to learn for people with background in python.

Now we explain the structure of our language. We start from the top of our
abstract syntax tree (AST).
The root of an AST is either a `condition` or a `target`. Both link directly to
a `statement` (l.2).

A `statement` is either `linked`, `single`, or a `comparison` (l.4).
`linked` is a statement combined with another statement 
using a logical operator (e.g. `and` or `or`) (l.5).
A comparison is done between two attributes (l.6).
An attribute is either an subject, object, environment or access attribut,
or an constant directly written into the grammar, called lit (for literal).
Non literals start with `subject.`, `object.`, `environment.` or `access.`
followed by at least one word character (characters from a-z, A-Z, 0-9 or the underscore
`_`) or dot `.` (l.9-l.15).
Literal attributes can either be integers, an string (quoted with double or single
quotes), a boolean value (`True` or `False`) or a list (in python notation) (l.19-27).
Nested lists are possible.
In quoted strings every character is allowed, except the quotation character (ll. 25).
Comparson operators are `>`, `<`, `==`, `!=`, `startswith`, `matches` (l.32).

`single` is either directly an attribut or an attribut with an unary operator (uop) (l.7).
The only unary operator currently allowed is  `exists`.

After the rule is parsed, we must return, given the abstract syntax tree and the attributes,
a boolean value. We explain this in :ref:`ac_entity_evaluation`

Parser
------

The parser has the task to turn a string of the language into a boolean value.
The parser is given only the string and the evaluation context.
We define two functions: `check_target` and `check_conditition` which either
transform a target string into a boolean value or a condition string.

Grammar Reference
-----------------

This is the actual grammar that is used to parse the condition and target
statements. The grammar is parsed using lark, which uses a syntax similar
to the EBNF.

.. literalinclude:: /oidcproxy/resources/grammar.lark
   :language: jsgf
   :linenos:

Obligations
============

.. uml::
   :scale: 40 %

   !include docs/overview.plantuml
   
   remove object
   remove user
   remove oidcprovider
   remove OIDC
   remove acentities
   remove objinf
   remove environment

Obligations are actions that must be executed successfully after the evaluation
of AC hierarchy. Every AC entity can specify a set of obligations which must
be executed if the target specifier of that entity was matched.
Obligations are called in the same way as the environment attribute setter,
i.e. all obligations inherit from the same class and are collected in a mapping
from name to class.
After the access control decision, all obligations are run, i.e. the run method
of the Obligation object is executed with the effect, with the access control context
and their configuration specified in the configuration file.
An obligation must return a boolean value. The access is only granted and the
object delivered if all obligations returned `true`.

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
   remove oidcproxy.plugins.EnvironmentDict
   remove oidcproxy.plugins.ObjectDict
   remove oidcproxy.plugins.PrioritizedItem
   remove oidcproxy.plugins._lib.EnvironmentAttribute
   remove oidcproxy.plugins._lib.ObjectSetter
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

