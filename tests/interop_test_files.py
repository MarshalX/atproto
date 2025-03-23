import os
from pathlib import Path
from typing import List

# Test data sourced directly from bluesky-social/atproto repo:
# https://github.com/bluesky-social/atproto/tree/main/interop-test-files/syntax
INTEROP_TEST_FILES_DIR = Path(os.path.join(Path(__file__).parent, 'interop-test-files', 'syntax'))


def get_test_cases(filename: str) -> List[str]:
    """Get non-comment, non-empty lines from an interop test file.

    Important: Preserves whitespace in test cases. This is critical for
    format validators where leading/trailing/internal whitespace makes a
    value invalid. For example, ' 1985-04-12T23:20:50.123Z' (with leading space)
    should be invalid for datetime validation.

    Args:
        filename: Name of the test file to read from interop test files directory

    Returns:
        List of test cases with original whitespace preserved
    """
    return [
        line
        for line in INTEROP_TEST_FILES_DIR.joinpath(filename).read_text().splitlines()
        if line and not line.startswith('#')
    ]
