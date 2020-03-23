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
   !include docs/concepts/seq_ps_evaluation.puml

.. uml::
   :scale: 60%

   caption Sequence diagram for policy evaluation
   skinparam DiagramBorderThickness 2
   !include docs/concepts/seq_p_evaluation.puml


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

.. literalinclude:: /oidcproxy/resources/grammar.lark
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

   !include docs/overview.plantuml
   
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

