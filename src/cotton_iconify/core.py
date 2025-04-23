"""Core functionality for processing Iconify icons."""

from typing import Dict, Any, Optional


def resolve_icon(icon_data: Dict[str, Any], icon_set: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve icon data, applying any default values from the icon set.

    Args:
        icon_data: Icon data to resolve
        icon_set: Icon set data with potential default values

    Returns:
        Dict: Resolved icon data with all properties
    """
    # Default icon properties
    default_props = {
        "width": 16,
        "height": 16,
        "left": 0,
        "top": 0,
        "hFlip": False,
        "vFlip": False,
        "rotate": 0,
    }

    # Apply icon set defaults
    for prop in default_props:
        if prop in icon_set:
            default_props[prop] = icon_set[prop]

    # Apply icon specific values
    resolved = default_props.copy()
    for prop, value in icon_data.items():
        resolved[prop] = value

    return resolved


def resolve_alias(
    alias_data: Dict[str, Any],
    icons: Dict[str, Any],
    icon_set: Dict[str, Any],
    resolved_aliases: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Resolve alias by merging with parent icon data.

    Args:
        alias_data: Alias data to resolve
        icons: Dictionary of icons
        icon_set: Full icon set data
        resolved_aliases: Already resolved aliases for recursive resolution

    Returns:
        Dict or None: Resolved alias data or None if parent not found
    """
    if resolved_aliases is None:
        resolved_aliases = {}

    parent = alias_data.get("parent")
    if not parent:
        return None

    # Get parent data
    if parent in resolved_aliases:
        parent_data = resolved_aliases[parent]
    elif parent in icons:
        parent_data = resolve_icon(icons[parent], icon_set)
    else:
        return None

    # Create a copy of parent data
    resolved = parent_data.copy()

    # Apply transformations from alias (XOR for flips, addition modulo 4 for rotation)
    if "hFlip" in alias_data:
        resolved["hFlip"] = bool(alias_data["hFlip"]) != bool(
            resolved.get("hFlip", False)
        )

    if "vFlip" in alias_data:
        resolved["vFlip"] = bool(alias_data["vFlip"]) != bool(
            resolved.get("vFlip", False)
        )

    if "rotate" in alias_data:
        resolved["rotate"] = (resolved.get("rotate", 0) + alias_data["rotate"]) % 4

    # Override any direct properties (except transformations that were already handled)
    for key, value in alias_data.items():
        if key not in ["parent", "hFlip", "vFlip", "rotate"]:
            resolved[key] = value

    return resolved


def resolve_all_aliases(icon_set: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Resolve all aliases in an icon set.

    Args:
        icon_set: The icon set with icons and aliases

    Returns:
        Dict: A dictionary of resolved alias data
    """
    icons = icon_set.get("icons", {})
    aliases = icon_set.get("aliases", {})

    resolved_aliases = {}
    for alias_name, alias_data in aliases.items():
        resolved = resolve_alias(alias_data, icons, icon_set, resolved_aliases)
        if resolved:
            resolved_aliases[alias_name] = resolved

    return resolved_aliases
