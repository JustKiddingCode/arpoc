.. _ac_entity_evaluation:

AC Entity Evaluation
====================

After the parser created the AST, we want a boolean value.

The following figure shows the AST for the condition `subject.email == 'email@example.com' and exists object.var`.
We show the transformation process with the AC context that only contains the key `email` in the subject mapping
with the value `email@example.com`.

.. figure:: /docs/gen/ac_eval_before_transformers.png

   Example of the abstract syntax tree (AST) of the condition `subject.email == 'email@example.com' and exists object.var`

Given this AST and the access context (the attributes), we now must return a boolean
value. We do this by transforming the AST step by step, starting at the leaves.
This is done by transformers.
A transformer is called automatically by the parser library lark and can edit
the leave arbitrarily.

Broadly classified, there are the attributes transformer, operator transformers,
middle level and top level transformers. To increase performance of the tree evaluation,
all transformers are combined and called as needed.
To illustrate the how the system works, we show the result of every transformer seperately.

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
   remove oidcproxy.ac.common.Effects
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


Attribute transformers (`TransformAttr`) replace the Token
object with the attribute key by the real attribute.
Exemplarily we show the substition of subject attributes.

.. literalinclude:: /oidcproxy/ac/parser.py
   :pyobject: TransformAttr.subject_attr
   :linenos:
   :lines: 1,4-12

The args are the children of the `subject_attr` node. There is only one
child, the Token object with the string 'email'.
To support dictionary lookups we split this key string at the dots and use a
lambda function to recursively walk the dictionary.
The lambda function expects two arguments: an dictionary and a key.
If the dictionary typ is a mapping, i.e. we can access elements with a key,
we return this dictionary lookup. This lambda function is executed for every element
in the split-up key list by the reduce function.
The start dictionary is in this case the subject atribute dictionary.
If the function was not able to find a attribute an exception is raised.

This is why we have the special `exists` transformer. 
The `exists` tranformer is run before all other transformers.
It transforms a `uop` node to the *string* `exists` if and only if the text in the token
is literally 'exists'. Furthermore a `single` node is transformed if and only if
the first child is the *string* `exists`.
The attributes are substituted using the previously described transformer functions
but the exeptions thrown by missing attributes are catched and in the case of
an exception  exists evaluated to *False* else to *True*.

.. figure:: /docs/gen/ac_eval_after_exists.png

   AST after the run of the exists transformer 

.. figure:: /docs/gen/ac_eval_after_attr.png

   AST after the run of the attribute transformer



Operator transformers replace the Token object with a function reference.
Every operator is implemented in its own class. Through inheritance, some
type checks can be performed, e.g. the `BinarySameTypeOperator` checks
if the types of the operators are the same and the `BinaryStringOperator` checks
if both operands are strings.
This function reference is then executed by the middle level transformers.

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
   remove oidcproxy.ac.common.Effects
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
   remove oidcproxy.ac.parser.ExistsTransformer
   remove oidcproxy.ac.lark_adapter.MyTransformer
   remove oidcproxy.ac.lark_adapter.CombinedTransformer
   remove oidcproxy.ac.parser.MiddleLevelTransformer
   remove oidcproxy.ac.parser.OperatorTransformer
   remove oidcproxy.ac.parser.TopLevelTransformer
   remove oidcproxy.ac.parser.TransformAttr
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

Applicated to our example, the operator tokens got replaced by a class.

.. figure:: /docs/gen/ac_eval_after_op.png

   AST after the run of the operator transformer

The nodes `comparison`, `single` and `linked` are transformed with 
middle level transformers. For the linked statement its important that 
it does not change the tree if
the children are not already transformed.

.. figure:: /docs/gen/ac_eval_after_mlt.png

   AST after the run of the middle level transformer

Top level transformers, like statement,  condition or target,
then pass the results of middle level transformers through, but forcing the value
to be boolean.


.. figure:: /docs/gen/ac_eval_after_tlt.png

   AST after the run of the top level transformer


For the `linked` statement we need to re-apply a middle level transformer.

.. figure:: /docs/gen/ac_eval_after_tlt_mlt.png
   :scale: 40%

   AST after the run of the middle level transformer



Conflict Resolution
====================


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
