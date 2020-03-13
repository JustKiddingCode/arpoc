.. _ac_entity_evaluation:

AC Entity Evaluation
====================

Consider the figure below.

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
For didactic reasons, we show the result of every transformer seperately.

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

In our example, `comparison`, `single` and `linked` are middle level transformers.
For the linked statement its important that it does not change the tree if
the children are not already transformed.
Top level transformers, like statement,  condition or target,
then pass the results of middle level transformers through, but forcing the value
to be boolean.


A special case is however the `exists` operator. Normally, missing attributes throw an
exception. This however, ends the evaluation of the tree and therefore is not
suited to what the user would expect with this operator.
For this, we used a special transformer that is run before all other transformers.
It transforms a `uop` node to the *string* `exists` if and only if the text in the token
is literally 'exists'. Furthermore a `single` node is transformed if and only if
the first child is the *string* `exists`.
The attributes are substituted using the previously described transformer functions
but the exeptions thrown by missing attributes are catched and in the case of
an exception  exists evaluated to *False* else to *True*.

The effects all transformers have is shown in the next figures.

.. figure:: /docs/gen/ac_eval_after_exists.png

   AST after the run of the exists transformer 

.. figure:: /docs/gen/ac_eval_after_attr.png

   AST after the run of the attribute transformer

.. figure:: /docs/gen/ac_eval_after_op.png

   AST after the run of the operator transformer

.. figure:: /docs/gen/ac_eval_after_mlt.png

   AST after the run of the middle level transformer

.. figure:: /docs/gen/ac_eval_after_tlt.png

   AST after the run of the top level transformer

.. figure:: /docs/gen/ac_eval_after_tlt_mlt.png
   :width: 60%

   AST after the run of the middle level transformer
