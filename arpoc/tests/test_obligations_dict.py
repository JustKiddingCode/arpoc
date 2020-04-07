
import arpoc.plugins

from arpoc.ac.common import Effects

from unittest.mock import patch

import os

import pytest

dummy_plugins = os.path.join(os.path.dirname(__file__), "resources", "dummy_plugins")

print(arpoc.plugins.config)
#[dummy_plugins], create=True)

@patch('arpoc.plugins.config.cfg')
def test_obl_dict(patcher):
    patcher.proxy.plugin_dirs = [dummy_plugins]
    arpoc.plugins.import_plugins()
    odict = arpoc.plugins.ObligationsDict()
    odict.run_all(["obl_dummy"], Effects.GRANT, {}, {})
    with pytest.raises(ValueError):
        odict.run_all(["obl_missing"], Effects.GRANT, {}, {})


