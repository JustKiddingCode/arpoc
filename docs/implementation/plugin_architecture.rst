.. _implementation_plugin:

Plugin Architecture
===================

.. uml::
   :scale: 40 %

   !include docs/overview.plantuml
   
   hide oidcprovider
   hide user
   hide acentities
   hide object

We used a modular design, so that users can modify the behaviour to their needs.
As above figure illustrates, there are three possibilities to use plugins:

* Obligations
* Environment setters
* Object Setters

For each type the plugin must inherit from a specific class and the python
module must be placed in specific configurable folder.

Obligations
-----------

An obligation plugin gets the result of the access control evaluation and the
context data and must return a boolean.
If an obligation does not return `True` then access is denied.
The obligation class must set the class attribute `name` and can referenced
by it from the access control entities.

Included obligations are:

* TODO
* TODO

Environment setters
-------------------

Environment setters are run when the evaluation process requests 
a specific environment attribute, referenced
by the class attribute `target`.
The return value of the environment setter is then used every time
the environment attribute is requested.

Included environment setters are:

* TODO
* TODO

Object setters
--------------

Object setters are run when an object attribute is requested and not found.
Then, every enabled object setter is run in the order of their priority,
starting with the smallest priority.
Object setters are initialized with their configuration data and get the object
data as input.
One object setter can set as many attributes of the object as needed, though
object setters running later will override the values of previous ones.

Included object setters are:

* TODO
* TODO
