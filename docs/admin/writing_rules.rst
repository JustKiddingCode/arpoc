Writing Access Control Rules
============================


Every service has a policy set assigned that is evaluated and based on the
outcome the access to the service is either granted or denied.

A simple example:
-----------------

Consider you just want to proxy a service with no further authentication
or authorisation.
Nonetheless you need to specify a policy set, a policy and a rule for the service.

.. code-block:: json

        {
        "com.example.policysets.default": {
                "Type": "PolicySet",
                "Description": "Default Policy Set",
                "Target": "True",
                "Policies": ["com.example.policies.default"],
                "PolicySets": [],
                "Resolver": "ANY"
        },
        "com.example.policies.default": {
                "Type": "Policy",
                "Description": "Default Policy",
                "Target" : "True",
                "Rules" : [ "com.example.rules.default"],
                "Resolver": "ANY"
        },
        "com.example.rules.default" : {
                "Type": "Rule",
                "Target": "True",
                "Description": "Default Rule",
                "Condition" : "True",
                "Effect": "GRANT"
        }
        }

Now let's do more complicated stuff.
Suppose we wan't a public available website, but the subfolder '/admin'
should be only accessible by an user that has an email that starts with 'admin@'.
So we add a *rule* with the target specifier `object.url startswith '/admin'`.
If the path does not start with '/admin' then the rule is not evaluated.
For the condition we choose analogue `subject.email startswith 'admin@'`
Now the rule fulfills our requirements, aka it is evaluated to `DENY`.
But after adding the rule to the `Rules` list of our policy, 
still every user has access to the
'/admin' folder.
This is because the rule 'com.example.rules.default' evaluates to `GRANT`.
The task of the policy resolver is to turn the results of all evaluated
rules to a single effect.
The `ANY` resolver return `GRANT` as soon as any rule evaluated to `GRANT`.
To achieve the effect the want we can use the `AND` resolver.

The resulting access control entities are:

.. code-block:: json

        {
        "com.example.policysets.default": {
                "Type": "PolicySet",
                "Description": "Default Policy Set",
                "Target": "True",
                "Policies": ["com.example.policies.default"],
                "PolicySets": [],
                "Resolver": "ANY"
        },
        "com.example.policies.default": {
                "Type": "Policy",
                "Description": "Default Policy",
                "Target" : "True",
                "Rules" : [ "com.example.rules.default", "com.example.rules.admin"],
                "Resolver": "AND"
        },
        "com.example.rules.default" : {
                "Type": "Rule",
                "Target": "True",
                "Description": "Default Rule",
                "Condition" : "True",
                "Effect": "GRANT"
        },
        "com.example.rules.admin" : {
                "Type": "Rule",
                "Target": "object.url startswith '/admin'",
                "Description": "Grant access to /admin folder only to admins",
                "Condition" : "subject.email startswith 'admin@'",
                "Effect": "GRANT"
        }
        }


By now, you should understand the idea behind the access control entity hierarchy,
and how they get to the result.
Let's look more on the details of the condition and target language.

Condition and target language
-----------------------------

The language is similar to Python.
You have four dictionaries (subject, object, environment and access) and can
compare them against constants or each other.
The subject dictionary is filled with information from the Userinfo
Endpoint of the OpenID Connect Provider.
The object dictionary is filled with information of the object, like the url.
This can be enhanced by plugins.
The environment dictionary is completely filled with the use of plugins.
The plugins for the environment dictionary must contain a target variable
and are only run when the target variable is evaluated, while the object plugins
are run before the access decision is made.
The order of the object plugins is based on a priority that has to be submitted
in the configuration file.
For every proxied service a different set of object plugins can be enabled and
different priorities choosen.



Attributes
**********

An attribute is either a subject, an object, an environment or a literal
attribute.
As literal attributes integers, booleans or lists are supported.
Booleans are either "True" or "False" including the quotation marks.
List statements are supported like in Python, but limited to only flat
lists. So '["elem1", "elem2", "elem3"]' is supported, '["elem1,["elem2","elem3"]]'
not.
Dictionaries are supported, but keys are limited to word characters (a-z, A-Z, 0-9,_).
Access to dictionaries looks like this: `access.headers.authorization`.
Here the first dot is the usual attribute getter (access, subject, object, environment),
the second goes one level deeper in the dictionary. The statement gets translated
into `access['headers']['authorization']`.


Comparison Operators
********************

The operators ">","<","==","!=" and work as in Python, or in any other C-like
language.
For strings the operators "startswith" (literal prefix) and "matches" (regex)
are supported.
"abcde" startswith "ab" will evaluate to True as well as
"'01:02:03' matches '[0-9]{2}:[0-9]{2}:[0-9]{2}'".
Statements can me connected using "and" and "or".


Examples
***************

.. code-block:: txt

   '/group1' in subject.groups
   subject.age > 18
   subject.email in object.allowed

Grammar Reference
*****************

This is the actual grammar that is used to parse the condition and target
statements. The grammar is parsed using lark.

.. literalinclude:: /oidcproxy/resources/grammar.lark
   :language: jsgf

