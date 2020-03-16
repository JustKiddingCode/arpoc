Concepts
===================

This chapter presents the basic concepts and design of our reverse proxy.
It starts with the explanation of the policy enforcement point, i.e. the
interface to the user, continues with a description of access control elements
including the evaluation process and the access control language.
After that, it shows the concepts of attribut
retrieval and focuses on what objects can be protected with this proxy and how
the object delivery is done after successful evaluation.
This chapter ends with considerations about caching and how caching is used
in this proxy.

.. toctree::
        interface
        ac_hierarchy
        ac_context
        policy_information
        object
        object_delivery
        caching
