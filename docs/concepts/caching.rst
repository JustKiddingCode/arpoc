Caching
============================

Reverse proxies should deliver their websites as fast as possible.
This means that the latency should be as low as possible and is usually done
by caching. With caching we mean to save the results of an action, like requesting a
specific resource or calculating or performing a CPU-intensive task.

There are several scenarios where caching could be used in the context of a
reverse proxy.
In the following we discuss two scenarios: Caching of the access control
entities evaluation and caching of the access control context.

Caching of the access control evaluation results between two different accesses
is infeasible.
Even if the subject attributes have not changed, the environment or
information about the object could have changed. Therefore the reverse proxy
must evaluate the hierarchy every time and request environment variables or
object variables every time.

In an access control decision process the evaluation of each rule, policy and
policy set is cached. Therefore in a case that e.g. a rule is included in multiple
policies and would need evaluation multiple times, it is only
evaluated once.

Caching of user information is done in dependency of the access key.
For each access key, the information about an user is only collected once and
then cached until the access key gets invalid.
In the case of a long-lifetime session the information gets therefore updated
when the access key gets renewed with the new renewal key.
