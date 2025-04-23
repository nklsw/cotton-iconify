"""Command-line interface for cotton-iconify."""

import argparse
import os
import sys
from urllib.parse import urljoin

from cotton_iconify.utils import fetch_json
from cotton_iconify.generators import generate_icon_file, generate_all_icons


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate Django component SVG files from Iconify JSON files."
    )
    parser.add_argument(
        "prefix", help='Icon set prefix (e.g., "brandico" for brandico.json)'
    )
    parser.add_argument(
        "icon", nargs="?", help="Optional: specific icon name to generate"
    )
    parser.add_argument(
        "--all", "-a", action="store_true", help="Generate all icons from the set"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output directory for SVG files (if not specified, uses templates/cotton/<icon-set>)",
    )
    parser.add_argument(
        "--source",
        "-s",
        default="https://github.com/iconify/icon-sets/blob/master/json/",
        help="Source URL for JSON files",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Overwrite existing files without asking",
    )
    parser.add_argument(
        "--file-prefix",
        "-p",
        help='Prefix to add to generated filenames (e.g., "icon" for icon-name.html)',
    )
    return parser.parse_args()


def main() -> None:
    """
    Main function to run the CLI application.

    This function:
    1. Parses command line arguments
    2. Fetches the icon set JSON
    3. Sets up the output directory
    4. Generates the icon file(s)
    """
    args = parse_args()

    # Construct URL for JSON file
    json_url = urljoin(args.source, f"{args.prefix}.json")

    # Fetch and parse JSON
    print(f"Fetching {json_url}...")
    icon_set = fetch_json(json_url)

    # Determine output directory
    if args.output:
        # If output is explicitly provided, use it exactly as specified
        output_dir = args.output
    else:
        # Default: use templates/cotton/<icon-set>
        output_dir = os.path.join(
            "templates", "cotton", icon_set.get("prefix", args.prefix)
        )

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Set overwrite_all based on force flag
    overwrite_all = True if args.force else None

    # Get file prefix (default to empty string if not provided)
    file_prefix = args.file_prefix or ""

    # Check if we're generating all icons or just one
    if args.icon and not args.all:
        # Generate a single icon
        success, _ = generate_icon_file(
            args.icon, icon_set, output_dir, overwrite_all, file_prefix
        )
        if not success:
            sys.exit(1)
    else:
        # Generate all icons
        generate_all_icons(icon_set, output_dir, overwrite_all, file_prefix)


if __name__ == "__main__":
    main()
