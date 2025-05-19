"""
Test fix script to run and make the tests compatible with the new JSON string response format.
"""

import json
import os
import re


def fix_test_toc_service():
    """Fix the TOC service tests to work with string responses."""
    filepath = "tests/services/test_toc_service.py"
    with open(filepath, "r") as f:
        content = f.read()

    # Update all content == "Sample TOC content" assertions
    pattern = r'assert toc_content == "Sample TOC content"'
    replacement = 'assert "Sample TOC content" in toc_content'
    content = re.sub(pattern, replacement, content)

    # Fix the save_toc_to_file assertions to use toc_content directly
    pattern = r'toc_service_with_mocks.pdf_service.save_toc_to_file.assert_called_once_with\(\n        "Sample TOC content"'
    replacement = "toc_service_with_mocks.pdf_service.save_toc_to_file.assert_called_once_with(\n        toc_content"
    content = re.sub(pattern, replacement, content)

    pattern = r'toc_service_with_mocks.pdf_service.save_toc_to_file.assert_called_once_with\(\n        "Sample TOC content", output_file'
    replacement = "toc_service_with_mocks.pdf_service.save_toc_to_file.assert_called_once_with(\n        toc_content, output_file"
    content = re.sub(pattern, replacement, content)

    # Write updated content back to file
    with open(filepath, "w") as f:
        f.write(content)

    print(f"Updated {filepath} to handle string responses")


def fix_test_openai_service():
    """Fix the OpenAI service tests to expect string responses."""
    filepath = "tests/services/test_openai_service.py"
    with open(filepath, "r") as f:
        content = f.read()

    # Update assertion to check string instead of dict
    pattern = r"assert isinstance\(result, dict\)"
    replacement = "assert isinstance(result, str)"
    content = re.sub(pattern, replacement, content)

    # Write updated content back to file
    with open(filepath, "w") as f:
        f.write(content)

    print(f"Updated {filepath} to handle string responses")


if __name__ == "__main__":
    fix_test_toc_service()
    fix_test_openai_service()
    print("All test files updated successfully.")
