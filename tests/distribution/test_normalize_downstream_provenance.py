import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("normalize-downstream-provenance.py")
CANONICAL_ENGINE_NAME = "rcpch/rcpchgrowth-python"
COMMIT = "a" * 40


def run_normalizer(golden_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(golden_dir), "4.6.2", COMMIT],
        capture_output=True,
        check=False,
        text=True,
    )


def test_normalizes_legacy_and_canonical_engine_provenance(tmp_path):
    golden = tmp_path / "measurement.json"
    golden.write_text(
        json.dumps(
            {
                "measurements": [
                    {
                        "provenance": {
                            "calculation_engine": {
                                "name": "rcpchgrowth",
                                "version": "4.6.0",
                                "commit": "old",
                            }
                        }
                    },
                    {
                        "provenance": {
                            "calculation_engine": {
                                "name": CANONICAL_ENGINE_NAME,
                                "version": "4.6.1",
                                "commit": "previous",
                            }
                        }
                    },
                ]
            }
        )
    )

    result = run_normalizer(tmp_path)

    assert result.returncode == 0, result.stderr
    assert result.stdout == "Normalized 2 downstream provenance records\n"
    engines = [
        measurement["provenance"]["calculation_engine"]
        for measurement in json.loads(golden.read_text())["measurements"]
    ]
    assert engines == [
        {"name": CANONICAL_ENGINE_NAME, "version": "4.6.2", "commit": COMMIT},
        {"name": CANONICAL_ENGINE_NAME, "version": "4.6.2", "commit": COMMIT},
    ]


def test_preserves_unrelated_engine_provenance(tmp_path):
    golden = tmp_path / "measurement.json"
    original = {
        "provenance": {
            "calculation_engine": {
                "name": "another-engine",
                "version": "1.0.0",
                "commit": "unchanged",
            }
        }
    }
    golden.write_text(json.dumps(original))

    result = run_normalizer(tmp_path)

    assert result.returncode != 0
    assert "No supported rcpchgrowth provenance found" in result.stderr
    assert json.loads(golden.read_text()) == original
