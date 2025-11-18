"""Output formatting utilities."""

import json
from typing import Any, List, Dict, Optional
from enum import Enum


class OutputFormat(Enum):
    """Output format options."""
    UNIX = "unix"        # Line-oriented, streamable
    JSON = "json"        # Pretty-printed JSON
    LLM = "llm"          # Human-readable for LLMs


def format_output(
    data: Any,
    format_type: OutputFormat = OutputFormat.UNIX,
    fields: Optional[List[str]] = None,
    headers: Optional[List[str]] = None
) -> str:
    """Format data for output.

    Args:
        data: Data to format (dict, list of dicts, or string)
        format_type: Output format (unix, json, llm)
        fields: Fields to include for dict/list (order matters)
        headers: Header names to use instead of field names

    Returns:
        Formatted string ready to print
    """
    if format_type == OutputFormat.JSON:
        return _format_json(data)
    elif format_type == OutputFormat.UNIX:
        return _format_unix(data, fields, headers)
    elif format_type == OutputFormat.LLM:
        return _format_llm(data, fields, headers)
    else:
        raise ValueError(f"Unknown format: {format_type}")


def _format_json(data: Any) -> str:
    """Format data as pretty-printed JSON."""
    return json.dumps(data, indent=2, default=str)


def _format_unix(
    data: Any,
    fields: Optional[List[str]] = None,
    headers: Optional[List[str]] = None
) -> str:
    """Format data as line-oriented output suitable for piping.

    Tab-separated values, one item per line.
    """
    if isinstance(data, dict):
        # Single object: output as tab-separated values
        if fields:
            values = [str(data.get(f, "")) for f in fields]
        else:
            values = [str(v) for v in data.values()]
        return "\t".join(values)

    elif isinstance(data, list):
        if not data:
            return ""

        # List of dicts
        if isinstance(data[0], dict):
            if not fields:
                # Use keys from first item
                fields = list(data[0].keys())

            lines = []
            for item in data:
                values = [str(item.get(f, "")) for f in fields]
                lines.append("\t".join(values))
            return "\n".join(lines)

        # List of simple values
        else:
            return "\n".join(str(item) for item in data)

    else:
        return str(data)


def _format_llm(
    data: Any,
    fields: Optional[List[str]] = None,
    headers: Optional[List[str]] = None
) -> str:
    """Format data in human-readable form optimized for LLMs."""
    if isinstance(data, dict):
        return _format_dict_llm(data, fields, headers)
    elif isinstance(data, list):
        return _format_list_llm(data, fields, headers)
    else:
        return str(data)


def _format_dict_llm(
    data: Dict[str, Any],
    fields: Optional[List[str]] = None,
    headers: Optional[List[str]] = None
) -> str:
    """Format a single dict as human-readable text."""
    lines = []
    if fields:
        items = [(h or f, data.get(f, "")) for h, f in zip(headers or fields, fields)]
    else:
        items = list(data.items())

    for key, value in items:
        if value:
            lines.append(f"{key}: {value}")

    return "\n".join(lines)


def _format_list_llm(
    data: List[Any],
    fields: Optional[List[str]] = None,
    headers: Optional[List[str]] = None
) -> str:
    """Format a list as human-readable text."""
    if not data:
        return "(empty)"

    if isinstance(data[0], dict):
        # List of dicts: numbered list with key details
        lines = []
        for i, item in enumerate(data, 1):
            lines.append(f"{i}. {_format_dict_llm(item, fields, headers)}\n")
        return "\n".join(lines)

    else:
        # Simple list: bulleted
        return "\n".join(f"• {item}" for item in data)
