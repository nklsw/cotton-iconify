"""SVG template generation functions."""

import os
import sys
from typing import Dict, Any, Tuple, Optional

from cotton_iconify.core import resolve_icon, resolve_alias, resolve_all_aliases
from cotton_iconify.utils import save_file


def to_snake_case(text: str) -> str:
    """
    Convert a kebab-case string to snake_case.

    Args:
        text: A string in kebab-case format

    Returns:
        str: The same string in snake_case format
    """
    return text.replace("-", "_")


def generate_svg_template(icon_data: Dict[str, Any]) -> str:
    """
    Generate Django component SVG template from icon data.

    Args:
        icon_data: Resolved icon data with all properties

    Returns:
        str: Django component SVG template
    """
    # Extract required properties
    body = icon_data.get("body", "")
    width = icon_data.get("width", 16)
    height = icon_data.get("height", 16)
    left = icon_data.get("left", 0)
    top = icon_data.get("top", 0)
    hFlip = icon_data.get("hFlip", False)
    vFlip = icon_data.get("vFlip", False)
    rotate = icon_data.get("rotate", 0)

    # Calculate viewBox
    view_box = f"{left} {top} {width} {height}"

    # Start the Django component template with default values in c-vars
    template = f'<c-vars width="{width}" height="{height}" viewBox="{view_box}" />\n\n'

    # Begin the SVG with Django template variables
    template += '<svg {{ attrs }} xmlns="http://www.w3.org/2000/svg" '
    template += 'width="{{ width }}" height="{{ height }}" viewBox="{{ viewBox }}">\n'

    # Apply transformations if needed
    if hFlip or vFlip or rotate:
        # Calculate the center of the icon
        center_x = width / 2
        center_y = height / 2

        # Create transform attribute (order: translate to center, rotate, flip, translate back)
        transform = f"translate({center_x} {center_y})"

        if rotate:
            angle = rotate * 90
            transform += f" rotate({angle})"

        scale_x = -1 if hFlip else 1
        scale_y = -1 if vFlip else 1
        if scale_x != 1 or scale_y != 1:
            transform += f" scale({scale_x} {scale_y})"

        transform += f" translate({-center_x} {-center_y})"

        template += f'  <g transform="{transform}">\n'
        template += f"    {body}\n"
        template += "  </g>\n"
    else:
        template += f"  {body}\n"

    template += "</svg>"

    return template


def generate_icon_file(
    icon_name: str,
    icon_set: Dict[str, Any],
    output_dir: str,
    overwrite_all: Optional[bool] = None,
    file_prefix: str = "",
    use_kebab: bool = False,
) -> Tuple[bool, Optional[bool]]:
    """
    Generate SVG template for a specific icon.

    Args:
        icon_name: Name of the icon to generate
        icon_set: Full icon set data
        output_dir: Output directory for the generated file
        overwrite_all: Whether to overwrite all existing files
        file_prefix: Prefix to add to generated filenames
        use_kebab: Whether to use kebab-case for filenames (default: snake_case)

    Returns:
        Tuple[bool, Optional[bool]]: Success status and updated overwrite_all value
    """
    icons = icon_set.get("icons", {})
    aliases = icon_set.get("aliases", {})

    # Prepare filename with prefix and separator
    filename = icon_name
    if not use_kebab:
        filename = to_snake_case(filename)

    if file_prefix:
        filename = f"{file_prefix}-{filename}"

    # Check if the icon exists in regular icons
    if icon_name in icons:
        resolved_data = resolve_icon(icons[icon_name], icon_set)
        template_content = generate_svg_template(resolved_data)

        file_path = os.path.join(output_dir, f"{filename}.html")
        overwrite_all = save_file(file_path, template_content, overwrite_all)

        print(
            f"Generated template for '{icon_name}' as '{filename}.html' in {output_dir}"
        )
        return True, overwrite_all

    # Check if the icon exists in aliases
    elif icon_name in aliases:
        # Resolve all required aliases
        resolved_aliases = {}
        for alias_name, alias_data in aliases.items():
            if alias_name == icon_name or resolved_aliases:  # Only resolve what we need
                resolved = resolve_alias(alias_data, icons, icon_set, resolved_aliases)
                if resolved:
                    resolved_aliases[alias_name] = resolved

        if icon_name in resolved_aliases:
            template_content = generate_svg_template(resolved_aliases[icon_name])

            file_path = os.path.join(output_dir, f"{filename}.html")
            overwrite_all = save_file(file_path, template_content, overwrite_all)

            print(
                f"Generated template for alias '{icon_name}' as '{filename}.html' in {output_dir}"
            )
            return True, overwrite_all

    print(
        f"Error: Icon '{icon_name}' not found in the '{icon_set.get('prefix')}' icon set",
        file=sys.stderr,
    )
    return False, overwrite_all


def generate_all_icons(
    icon_set: Dict[str, Any],
    output_dir: str,
    overwrite_all: Optional[bool] = None,
    file_prefix: str = "",
    use_kebab: bool = False,
) -> None:
    """
    Generate templates for all icons in the set.

    Args:
        icon_set: Full icon set data
        output_dir: Output directory for the generated files
        overwrite_all: Whether to overwrite all existing files
        file_prefix: Prefix to add to generated filenames
        use_kebab: Whether to use kebab-case for filenames (default: snake_case)
    """
    icons = icon_set.get("icons", {})
    aliases = icon_set.get("aliases", {})

    print(
        f"Found {len(icons)} icons and {len(aliases)} aliases in {icon_set.get('prefix', '')} set"
    )

    # Resolve all aliases
    resolved_aliases = resolve_all_aliases(icon_set)

    # Generate templates for all icons
    count = 0

    # Process regular icons
    for icon_name, icon_data in icons.items():
        resolved_data = resolve_icon(icon_data, icon_set)
        template_content = generate_svg_template(resolved_data)

        # Prepare filename with prefix and separator
        filename = icon_name
        if not use_kebab:
            filename = to_snake_case(filename)

        if file_prefix:
            filename = f"{file_prefix}-{filename}"

        file_path = os.path.join(output_dir, f"{filename}.html")
        overwrite_all = save_file(file_path, template_content, overwrite_all)

        count += 1
        if count % 50 == 0:
            print(f"Generated {count} template files...")

    # Process aliases
    for alias_name, alias_data in resolved_aliases.items():
        template_content = generate_svg_template(alias_data)

        # Prepare filename with prefix and separator
        filename = alias_name
        if not use_kebab:
            filename = to_snake_case(filename)

        if file_prefix:
            filename = f"{file_prefix}-{filename}"

        file_path = os.path.join(output_dir, f"{filename}.html")
        overwrite_all = save_file(file_path, template_content, overwrite_all)

        count += 1
        if count % 50 == 0:
            print(f"Generated {count} template files...")

    prefix_info = f" with prefix '{file_prefix}-'" if file_prefix else ""
    case_info = "kebab-case" if use_kebab else "snake_case"
    print(
        f"Successfully generated {count} Django component templates in {case_info}{prefix_info} in {output_dir}"
    )
