"""Test for medical terminology enforcement."""

import subprocess
import sys
from pathlib import Path


def test_no_medical_terminology():
    """Test that no forbidden medical terminology exists in codebase."""
    script_path = Path(__file__).parent.parent / "scripts" / "check_medical_terms.py"
    
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
    )
    
    # Script returns 0 if no violations found, 1 if violations found
    assert result.returncode == 0, (
        f"Medical terminology check failed:\n{result.stdout}\n{result.stderr}"
    )
    
    # Verify success message in output
    assert "No forbidden medical terminology found" in result.stdout, (
        "Terminology check did not report success"
    )
