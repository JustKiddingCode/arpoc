Scopes
======

For more information about the workflow see :ref:`concepts_attribute_retrival_subject`.
To add self-defined scopes and the claims they provide you can add the `special_claim2scope`
parameter to your openid provider config. The parameter expects a mapping from
claim to a list of scopes.
For example, if a scope `agemapper` provides the claim `role` you can add

.. code-block:: yaml
   
   special_claim2scope:
       role:
           - agemapper
