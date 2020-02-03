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
************

To increase speed, two mechanisms apply:
The resolver gets the result as soon as as a policy is evaluated.
The resolver can abort the evaluation process if the result is fixed.
This can be useful if, e.g. the access is denied, as soon as one rule denied
the access.
