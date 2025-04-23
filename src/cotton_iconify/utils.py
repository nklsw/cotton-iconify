"""Utility functions for the cotton-iconify package."""

import json
import os
import sys
from typing import Dict, Any, Optional
import requests


def fetch_json(url: str) -> Dict[str, Any]:
    """
    Fetch and parse JSON from URL.

    Args:
        url: URL to fetch JSON from

    Returns:
        Dict: Parsed JSON data

    Raises:
        SystemExit: If fetching or parsing JSON fails
    """
    # Convert GitHub UI URL to raw content URL if needed
    if "github.com" in url and "/blob/" in url:
        url = url.replace("github.com", "raw.githubusercontent.com").replace(
            "/blob/", "/"
        )

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching JSON file: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}", file=sys.stderr)
        sys.exit(1)


def save_file(
    file_path: str, content: str, overwrite_all: Optional[bool] = None
) -> Optional[bool]:
    """
    Save content to file, checking for file existence.

    Args:
        file_path: Path to save the file
        content: Content to write to the file
        overwrite_all: Whether to overwrite all existing files

    Returns:
        bool or None: Updated overwrite_all value or None if skipped
    """
    if os.path.exists(file_path):
        # If we already have a global decision, use it
        if overwrite_all is not None:
            if not overwrite_all:
                print(f"Skipping existing file: {file_path}")
                return overwrite_all
            # else: will continue to overwrite
        else:
            # Ask user what to do
            response = input(
                f"File already exists: {file_path}. Overwrite? (y/n/all): "
            ).lower()
            if response == "n":
                print(f"Skipping file: {file_path}")
                return overwrite_all
            elif response == "all":
                overwrite_all = True
                print("Will overwrite all existing files")
            # else: will continue to overwrite this file

    # Write or overwrite the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return overwrite_all
