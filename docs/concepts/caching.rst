Caching
============================


You could think of several scenarios where cahing could be used.
In the following we discuss two scenarios: Caching of the access control
entities evaluation and caching of the access control context.
With access control context we mean the attributes about the user, the accessed
object, the environment attributes and information about the access itself.

Caching of the access control evaluation results between two different contexts is pointless.
Even if the subject attributes have not changed, the environment or
information about the object could have changed.

In an access control decision process the evaluation of each rule, policy and
policy set is cached. Therefore in a case that e.g. a rule is included in multiple
policies and would need evaluation multiple times, it still is only
evaluated once.

Caching of user information is done in dependency of the access key.
For each access key, the information about an user is only collected once and
then cached until the access key gets invalid.
In the case of a long-lifetime session the information gets therefore updated
when the access key gets renewed with the new renewal key.
