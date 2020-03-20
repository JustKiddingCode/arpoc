
Code Quality
============

To maintain and develop an application the code quality is of crucial importance.
Therefore the whole code base is annotated with type hints and unit tests cover
the core functionality.

pylint
-------

Keeping a consistent code style makes it easier for new developers to get familiar
with the code. Therefore the code style quality is measured with pylint (:cite:`pylint`).
`pylint` rates the source code as 7.23/10.

typing
--------

Our complete project uses Python type hints. This way static sanity checks can be
done to reduce the amount of bugs in the source code. An example for such a static
code check application is MyPy. The type hints are done with the typing module (:cite:`typing`)

pytest
------

Unit tests are done with pytest (:cite:`pytest`). The code coverage, i.e. the
ratio of lines of code that are covered is over 80%.
Performance important parts like the access control parser are also benchmarked,
i.e. it is measured how long it takes to evaluate a certain access control
hierarchy with given data.

