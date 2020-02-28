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
middle level and top level transformers. Attribute transformers replace the Token
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
This function reference is then executed by the middle level transformers.
In our example, `comparison`, `single` and `linked` are middle level transformers.
For the linked statement its important that it does not change the tree if
the children are not already transformed.
Top level transformers, like statement,  condition or target,
then pass the results of middle level transformers through, but forcing the value
to be boolean.

In the normal tree evaluation, all transformers are combined and called as needed.
For didactic reasons, we show the result of every transformer seperately.

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
