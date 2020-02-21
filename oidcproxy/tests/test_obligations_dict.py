
import oidcproxy.plugins

from oidcproxy.ac.common import Effects

from unittest.mock import patch

import os

import pytest

dummy_plugins = os.path.join(os.path.dirname(__file__), "resources", "dummy_plugins")

print(oidcproxy.plugins.config)
#[dummy_plugins], create=True)

@patch('oidcproxy.plugins.config.cfg')
def test_obl_dict(patcher):
    patcher.proxy.plugin_dirs = [dummy_plugins]
    oidcproxy.plugins.import_plugins()
    odict = oidcproxy.plugins.ObligationsDict()
    odict.run_all(["obl_dummy"], Effects.GRANT, {}, {})
    with pytest.raises(ValueError):
        odict.run_all(["obl_missing"], Effects.GRANT, {}, {})


