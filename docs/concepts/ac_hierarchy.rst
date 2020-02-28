************
AC Entities
************

.. uml::
   :scale: 40 %

   !include docs/overview.plantuml
   
   hide object
   hide user
   hide oidcprovider
   hide OIDC
   hide obligations
   hide objinf
   hide environment

Access Control Hierarchy
========================

We use 3 levels of access control entities.
The highest are policy sets, then policies and then rules.
Every policy set can contain other policy sets and/or policies.
Every policy can contain one or more rules.

Every entity (policy set, policy, rule) has an unique id, and a target.
In the evaluation process, an entity is only evaluated if the target is evaluated to true.
Policies and policy sets have a resolver to solve conflicts of the rule
evaluation. Rules have a condition and an effect.

Each service specifies an policy set which is evaluated on access.

Evaluation Process
------------------

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
^^^^^^^^^^^^

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

The design goals were:

* simple to read and write
* possibility of combined statements
* support for comparisons:

    * equals / not equals
    * greater/lesser (or equal)
    * string startswith
    * string matches regex

* support of the following datatypes:

    * numeral
    * string
    * dictionaries
    * lists

* syntatically similar to python

We start with a statement. A statement is either a linked, i.e. a statement
combined with another statement using a logical operator (e.g. `and` or `or`),
it is a comparison, i.e. an attribute compared to another attribut or, to
be similar to python a single attribut, possibly with an unary operator.

An attribut in this case denotes either a subject, an object, an access, an 
environment or a literal, i.e. an constant, directly into the rule written, attribute.
Literal attributes can either be integers, an string (quoted with double or single
quotes), a boolean value (`True` or `False`) or a list (in python notation).
Nested lists are possible.

The keys of an attribute must consist of word characters (a-z, A-Z, 0-9 or an underscore).
To access dictionaries, a dot `.` can be used.
In quoted keys, every character, except for the quoting character is allowed.

After the rule is parsed, we must return, given the abstract syntax tree and the attributes,
a boolean value. We explain this in :ref:`ac_entity_evaluation`

Grammar Reference
-----------------

This is the actual grammar that is used to parse the condition and target
statements. The grammar is parsed using lark, which uses a syntax similar
to the EBNF.

.. literalinclude:: /oidcproxy/resources/grammar.lark
   :language: jsgf
