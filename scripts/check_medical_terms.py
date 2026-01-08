"""Script to scan codebase for forbidden medical terminology."""

import re
from pathlib import Path

# Forbidden terms from non-medical-scope.md
FORBIDDEN_TERMS = [
    "disease",
    "diagnosis",
    "diagnose",
    "diagnostic",
    "treatment",
    "treat",
    "therapy",
    "therapeutic",
    "cure",
    "healing",
    "recovery",
    "patient",
    "patients",
    "clinical",
    "clinic",
    "medical",
    "medicine",
    "pathology",
    "pathological",
    "disorder",
    "condition",
    "symptom",
    "symptoms",
    "prognosis",
    "prognosticate",
    "health",
    "healthy",
    "unhealthy",
    "sick",
    "sickness",
    "normal",  # in medical context - but allow in code (normalize, etc.)
    "abnormal",  # in medical context
    "wellness",
    "unwell",
]

# Patterns to exclude (e.g., "normalize" is OK, "normal state" is not)
EXCLUDE_PATTERNS = [
    r"normalize",
    r"normalization",
    r"norm",
    r"abnormal",  # Only flag if used in medical context
]

# File extensions to check
CODE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".txt", ".json"}

# Directories to exclude
EXCLUDE_DIRS = {"__pycache__", ".git", "node_modules", ".venv", "venv", "env", "docs", "scripts"}

# Files to exclude (documentation explaining constraints)
EXCLUDE_FILES = {"context.md", "2context.md", "README.md", "check_medical_terms.py"}


def scan_file(file_path: Path) -> list[tuple[int, str, str]]:
    """
    Scan a file for forbidden terms.

    Args:
        file_path: Path to file

    Returns:
        List of (line_number, line_content, matched_term) tuples
    """
    violations = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line_lower = line.lower()

                # Check each forbidden term
                for term in FORBIDDEN_TERMS:
                    # Skip if in exclude pattern
                    if any(re.search(pattern, line_lower) for pattern in EXCLUDE_PATTERNS):
                        continue

                # Allow "health" in health check endpoints
                if term == "health" and ("health check" in line_lower or "/health" in line_lower):
                    continue

                # Check if term appears (as whole word or part of identifier)
                pattern = r"\b" + re.escape(term) + r"\b"
                if re.search(pattern, line_lower):
                    violations.append((line_num, line.strip(), term))

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return violations


def scan_directory(root_dir: Path) -> dict[Path, list]:
    """
    Scan directory for forbidden terms.

    Args:
        root_dir: Root directory to scan

    Returns:
        Dictionary mapping file paths to violations
    """
    all_violations = {}

    for file_path in root_dir.rglob("*"):
        # Skip excluded directories
        if any(excluded in file_path.parts for excluded in EXCLUDE_DIRS):
            continue

        # Only check code files
        if file_path.suffix not in CODE_EXTENSIONS:
            continue

        # Skip excluded files
        if file_path.name in EXCLUDE_FILES:
            continue

        # Skip if it's a binary file or can't be read
        if not file_path.is_file():
            continue

        violations = scan_file(file_path)
        if violations:
            all_violations[file_path] = violations

    return all_violations


def main():
    """Main function."""
    project_root = Path(__file__).parent.parent

    print("Scanning codebase for forbidden medical terminology...")
    print("=" * 60)

    violations = scan_directory(project_root)

    if not violations:
        print("✅ No forbidden medical terminology found!")
        return 0

    print(f"❌ Found violations in {len(violations)} file(s):\n")

    for file_path, file_violations in violations.items():
        print(f"\n{file_path.relative_to(project_root)}:")
        for line_num, line_content, term in file_violations:
            print(f"  Line {line_num}: '{term}' - {line_content[:80]}")

    print("\n" + "=" * 60)
    print(f"Total violations: {sum(len(v) for v in violations.values())}")
    return 1


if __name__ == "__main__":
    exit(main())
