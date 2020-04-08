************
AC Entities
************

.. uml::
   :scale: 40 %

   !include overview.plantuml
   
   remove object
   remove user
   remove oidcprovider
   remove OIDC
   remove obligations
   remove objinf
   remove environment

AC Entities allow users to granularly specify conditions and circumstances
that have to be met to allow or deny the access.
It follows the concepts of XACML, while we focused on increased readability and
easier creation. The user defines rules, policies or policy sets, which
in turn can define other objects like effects, obligations and conflict resolutions.
We first start with AC Effects, then explain the access control hierarchy focus
on conflict resolution and explain the evaluation process in depth.
Then we explain the access control language, i.e. the language the user can specify
the conditions with. The last element of AC entities are `obligations`, a way
the user can ensure that actions are taken after an access control decision.

Effects
========================

Effects define if the access should be granted (`GRANT`) or not (`DENY`).
Only rules define their effects directly, the effects of policies and policy
sets are determined with their conflict resolution.

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

Access Control Hierarchy
========================

.. uml::
   :scale: 40 %

   !include classes.plantuml
   remove arpoc.App
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

We use three levels of access control entities.
The highest in the hierarchy are policy sets, then policies and then rules.
Every entity (policy set, policy, rule) has an unique id (`entity_id`), 
a target,
and a list of obligations (`obligations`).
In the evaluation process, an entity is only evaluated if the target is evaluated to true.
The entity id is used by other entities to link to each other.
Every entity can furthermore provide a description which is used merely for
display purpose.

Definition contain relation
  An access control entity A contains a different access control entity B if
  B's id is listed in A's:

    * `policy_sets` if B is a policy set
    * `policies` if B is a policy
    * `rules` if B is a rule

  We say an access control entity B is contained in A if A contains B.
  Policy sets and policies can only be contained in policy sets, while rules
  can only be contained in policies.

Policies and policy sets specify a conflict resolution which is used to determine
the effect the policy has after the containing rules are evaluated.

Rules specify their condition in the access control language and an effect.
If a rules get evaluated and their target matched, the condition is evaluated
and if the condition got evaluated to `true`, their effect is returned if the
condition evaluated to `false` the opposite of their effect is returned.

Conflict Resolution
===================

.. uml::
   :scale: 40 %

   !include classes.plantuml
   remove arpoc.App
   remove arpoc.ac.AC_Container
   remove arpoc.ac.AC_Entity
   remove arpoc.ac.EvaluationResult
   remove arpoc.ac.Policy
   remove arpoc.ac.Policy_Set
   remove arpoc.ac.Rule
   remove arpoc.ac.common.Effects
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

In the evaluation process of a policy or a policy set `A`, the conflict resolver
of `A` gets notified each time an ac entity contained in `A` finished its evaluation
process.
The conflict resolution is called with the entity id and the result of the evaluation.
It can then decide if the evaluation process must continue or the result is fixed,
i.e. will not change with further evaluation.


Evaluation Process
==================

Each service specifies a policy set which is evaluated in order to decide if
access is granted or denied.
We start at the bottom of the hierarchy, the rules, continue with policies and
end with policy sets.

The process of evaluation of a rule R is as follows:

#. Check the target specifier. If False, abort
#. Check condition specifier. If True return Effect, else return the inverse of Effect.

The process of evaluation of a policy P is as follows:

#. Check the target specifier. If False, abort
#. For every rule R contained in P: Evaluate R.
#. Let `Res` be the list of results of every rule R in P:
   Run the conflict resolution A specified with `Res` and get result for policy P.

The process of evaluation of a policy set A is as follows:

#. Check the target specifier, if False, abort
#. For every policy set B contained in A: evaluate policy set B.
#. For every policy P contained in A: evaluate policy P.
#. Let `Res` be the list of results of every policy set and every policy in A:
   Run the conflict resolution A specified with `Res` and get result for policy set A.


Improvements
------------

To increase speed of the evaluation process we applied the following mechanism:
The resolver gets the result of a contained AC entity 
as soon as the AC entity finished evaluation.
The resolver can then abort the evaluation process if the result is fixed.
This can be useful if, e.g. the access should denied, as soon as one rule denied
the access.

We describe the algorithm more formally with the next two sequence diagrams.
The first diagram shows the evaluation of a policy set, while the second pictures
the evaluation of a policy including more details of the evaluation of a rule.

.. uml::
   :scale: 60%

   caption Sequence diagram for policy set evaluation
   skinparam DiagramBorderThickness 2
   !include concepts/seq_ps_evaluation.puml

.. uml::
   :scale: 60%

   caption Sequence diagram for policy evaluation
   skinparam DiagramBorderThickness 2
   !include concepts/seq_p_evaluation.puml


Access Control Language
=======================

Parser
------

The parser has the task to turn a string of the language into a boolean value.
The parser is given only the string and the evaluation context.
We define two functions: `check_target` and `check_conditition` which either
transform a target string into a boolean value or a condition string.


Language description
--------------------

To specify the conditions that have to be met for an access, we wanted a language
that was simple to read and write, give us the possibility to combine conditions
and support multiple comparisons of strings as well as integers
(equals, not equal, greater/lesser (or equal), string startswith, string matches regex).
It should also support complex datatypes, such as dictionaries and lists, next to
basic datatypes (integers and strings).
Because Python is a widely known language and we implemented `arpoc` with Python
the syntax should be easy to learn for people with background in Python.
At the end of the evaluation a boolean value (`true` or `false`) should be returned.
This section focuses on the description of the abstract syntax tree (AST).
The transformation into a boolean value is descrbide in :ref:`ac_entity_evaluation`.

The following text is the actual grammar that is used to parse the condition and target
statements. The grammar is parsed using lark, which uses a syntax similar
to the EBNF (TODO:ref).

.. literalinclude:: /arpoc/resources/grammar.lark
   :language: jsgf
   :linenos:

We start from the top of our abstract syntax tree (AST).
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



Obligations
============

.. uml::
   :scale: 40 %

   !include overview.plantuml
   
   remove object
   remove user
   remove oidcprovider
   remove OIDC
   remove acentities
   remove objinf
   remove environment

Obligations are actions that must be executed successfully after the evaluation
of the AC hierarchy. Every AC entity can specify a set of obligations which must
be executed if the target specifier of that entity matched.
All obligations inherit from the same class and are collected in a mapping
from name to class.
After the access control decision, all obligations are run, i.e. the run method
of the Obligation object is executed with the effect, with the access control context
and their configuration specified in the configuration file.
An obligation must return a boolean value. The access is only granted and the
object delivered if all obligations returned `true`.

.. uml::
   :scale: 40 %

   !include classes.plantuml
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
   remove arpoc.plugins.EnvironmentDict
   remove arpoc.plugins.ObjectDict
   remove arpoc.plugins.PrioritizedItem
   remove arpoc.plugins._lib.EnvironmentAttribute
   remove arpoc.plugins._lib.ObjectSetter
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

