Policy Information Point
========================

Currently, the only location policies can be retrieved from is the local disk.
The ac entities must be in the JSON format.
In the JSON file a mapping from entity id (as string) to a dictionary is expected.
The expected keys in the dictionary are: `Type`, `Description`, `Target`, `Policies`
`PolicySets`, `Rules`, `Resolver`, `Obligations`, `Effect` and `Condition`.
`PolicySets`, `Policies`, `Rules` and `Obligations` are expected as array of strings, the
remaining keys are expected to be strings. The use of the keys is identical to
their description in TODOREF.

.. literalinclude:: /gen/ac_sample.json
   :linenos:

The AC Container allows to load a single json file or a directory of json files.
After the entity ids were loaded from disk, the `AC_Container` allows to 
get the ac entities by their ids.

json
----------

The JSON format is easy parseable and can be transmitted using the internet.
There are many parsers and tools for the JSON format.
All AC entities use the JSON format. The file can be parsed into dictionaries with
the Python native json module (:cite:`json`).
