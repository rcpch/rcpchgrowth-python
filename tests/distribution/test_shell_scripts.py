import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[2]


@pytest.mark.parametrize(
    "script",
    ["s/lint", "s/test-wheel", "s/test-downstream-wheel", "s/version++"],
)
def test_shell_script_syntax(script):
    subprocess.run(["bash", "-n", ROOT / script], check=True)
