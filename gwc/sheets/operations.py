"""Google Sheets API operations.

Implements spreadsheet read/write operations following the Sheets API v4.
Supports A1 notation for range specification.
"""

from typing import Any, List, Dict, Optional, Tuple
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
from pathlib import Path
from gwc.shared.auth import ALL_SCOPES

_sheets_service = None


def get_sheets_service():
    """Get or create Sheets API service."""
    global _sheets_service
    if _sheets_service is None:
        creds = _load_credentials()
        _sheets_service = build("sheets", "v4", credentials=creds)
    return _sheets_service


def _load_credentials() -> Credentials:
    """Load OAuth2 credentials from token file."""
    token_path = Path.home() / ".config" / "gwc" / "token.json"
    credentials_path = Path.home() / ".config" / "gwc" / "credentials.json"

    if not token_path.exists():
        raise Exception(
            "No token found. Run 'gwc auth' to authenticate first."
        )

    creds = Credentials.from_authorized_user_file(str(token_path), ALL_SCOPES)

    # Refresh if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed token
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())

    return creds


# ============================================================================
# Phase 1: Core Spreadsheet Operations
# ============================================================================


def create_spreadsheet(title: str, sheets: Optional[List[str]] = None) -> str:
    """Create a new blank spreadsheet.

    Args:
        title: Spreadsheet title
        sheets: Optional list of sheet names (defaults to ["Sheet1"])

    Returns:
        Spreadsheet ID
    """
    service = get_sheets_service()

    if sheets is None:
        sheets = ["Sheet1"]

    # Create spreadsheet with initial sheets
    body = {
        "properties": {"title": title},
        "sheets": [
            {"properties": {"title": sheet_name}} for sheet_name in sheets
        ],
    }

    result = service.spreadsheets().create(body=body).execute()
    return result["spreadsheetId"]


def get_spreadsheet(spreadsheet_id: str) -> Dict[str, Any]:
    """Get spreadsheet metadata and structure.

    Args:
        spreadsheet_id: Spreadsheet ID

    Returns:
        Spreadsheet metadata dict
    """
    service = get_sheets_service()
    result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    return result


def get_spreadsheet_title(spreadsheet_id: str) -> str:
    """Get spreadsheet title.

    Args:
        spreadsheet_id: Spreadsheet ID

    Returns:
        Spreadsheet title
    """
    spreadsheet = get_spreadsheet(spreadsheet_id)
    return spreadsheet.get("properties", {}).get("title", "Untitled")


def list_sheets(spreadsheet_id: str) -> List[Dict[str, Any]]:
    """List all sheets in spreadsheet.

    Args:
        spreadsheet_id: Spreadsheet ID

    Returns:
        List of sheet metadata dicts with keys: sheetId, title, gridProperties
    """
    spreadsheet = get_spreadsheet(spreadsheet_id)
    sheets = spreadsheet.get("sheets", [])

    result = []
    for sheet in sheets:
        props = sheet.get("properties", {})
        result.append(
            {
                "sheetId": props.get("sheetId"),
                "title": props.get("title"),
                "gridProperties": props.get("gridProperties", {}),
            }
        )

    return result


def read_range(
    spreadsheet_id: str,
    range_spec: str,
    value_render_option: str = "FORMATTED_VALUE",
    date_time_render_option: str = "FORMATTED_STRING",
) -> Dict[str, Any]:
    """Read values from a range.

    Args:
        spreadsheet_id: Spreadsheet ID
        range_spec: A1 notation range (e.g., "Sheet1!A1:C10")
        value_render_option: How to render values ("FORMATTED_VALUE" or "UNFORMATTED_VALUE" or "FORMULA")
        date_time_render_option: How to render dates ("SERIAL_NUMBER" or "FORMATTED_STRING")

    Returns:
        Dict with "range", "majorDimension", "values" keys
    """
    service = get_sheets_service()

    try:
        result = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id,
                range=range_spec,
                valueRenderOption=value_render_option,
                dateTimeRenderOption=date_time_render_option,
            )
            .execute()
        )
        return result
    except HttpError as e:
        raise Exception(f"Error reading range {range_spec}: {e}")


def read_ranges(
    spreadsheet_id: str,
    ranges: List[str],
    value_render_option: str = "FORMATTED_VALUE",
    date_time_render_option: str = "FORMATTED_STRING",
) -> List[Dict[str, Any]]:
    """Read values from multiple ranges.

    Args:
        spreadsheet_id: Spreadsheet ID
        ranges: List of A1 notation ranges
        value_render_option: How to render values
        date_time_render_option: How to render dates

    Returns:
        List of result dicts
    """
    service = get_sheets_service()

    try:
        result = (
            service.spreadsheets()
            .values()
            .batchGet(
                spreadsheetId=spreadsheet_id,
                ranges=ranges,
                valueRenderOption=value_render_option,
                dateTimeRenderOption=date_time_render_option,
            )
            .execute()
        )
        return result.get("valueRanges", [])
    except HttpError as e:
        raise Exception(f"Error reading ranges: {e}")


def write_range(
    spreadsheet_id: str,
    range_spec: str,
    values: List[List[Any]],
    value_input_option: str = "USER_ENTERED",
) -> Dict[str, Any]:
    """Write values to a range.

    Args:
        spreadsheet_id: Spreadsheet ID
        range_spec: A1 notation range
        values: 2D array of values (list of rows)
        value_input_option: "USER_ENTERED" (formulas interpreted) or "RAW"

    Returns:
        Response dict with updatedRange, updatedRows, updatedColumns, updatedCells
    """
    service = get_sheets_service()

    body = {"values": values}

    try:
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_spec,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
        return result
    except HttpError as e:
        raise Exception(f"Error writing range {range_spec}: {e}")


def append_range(
    spreadsheet_id: str,
    range_spec: str,
    values: List[List[Any]],
    value_input_option: str = "USER_ENTERED",
) -> Dict[str, Any]:
    """Append values to end of range (auto-expands).

    Args:
        spreadsheet_id: Spreadsheet ID
        range_spec: A1 notation range to append to
        values: 2D array of values
        value_input_option: "USER_ENTERED" or "RAW"

    Returns:
        Response dict with information about appended data
    """
    service = get_sheets_service()

    body = {"values": values}

    try:
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=range_spec,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
        return result
    except HttpError as e:
        raise Exception(f"Error appending to range {range_spec}: {e}")


def clear_range(spreadsheet_id: str, range_spec: str) -> Dict[str, Any]:
    """Clear values from a range.

    Args:
        spreadsheet_id: Spreadsheet ID
        range_spec: A1 notation range

    Returns:
        Response dict
    """
    service = get_sheets_service()

    try:
        result = (
            service.spreadsheets()
            .values()
            .clear(spreadsheetId=spreadsheet_id, range=range_spec)
            .execute()
        )
        return result
    except HttpError as e:
        raise Exception(f"Error clearing range {range_spec}: {e}")


def get_spreadsheet_stats(spreadsheet_id: str) -> Dict[str, Any]:
    """Get spreadsheet statistics.

    Args:
        spreadsheet_id: Spreadsheet ID

    Returns:
        Stats dict with sheet count, total cells, etc.
    """
    spreadsheet = get_spreadsheet(spreadsheet_id)

    sheets = spreadsheet.get("sheets", [])
    total_cells = 0
    sheet_count = len(sheets)

    for sheet in sheets:
        grid_props = sheet.get("properties", {}).get("gridProperties", {})
        rows = grid_props.get("rowCount", 0)
        cols = grid_props.get("columnCount", 0)
        total_cells += rows * cols

    return {
        "title": spreadsheet.get("properties", {}).get("title", "Untitled"),
        "spreadsheet_id": spreadsheet_id,
        "sheet_count": sheet_count,
        "total_cells": total_cells,
        "sheets": [
            {
                "title": s.get("properties", {}).get("title"),
                "rows": s.get("properties", {})
                .get("gridProperties", {})
                .get("rowCount", 0),
                "columns": s.get("properties", {})
                .get("gridProperties", {})
                .get("columnCount", 0),
            }
            for s in sheets
        ],
    }


def format_range_data(
    data: Dict[str, Any], format_type: str = "unix"
) -> str:
    """Format range data for output.

    Args:
        data: Range data from read_range
        format_type: "unix", "json", or "csv"

    Returns:
        Formatted string
    """
    if format_type == "json":
        return json.dumps(data, indent=2, default=str)

    if format_type == "csv":
        lines = []
        values = data.get("values", [])
        for row in values:
            # Escape values containing commas or quotes
            escaped = []
            for cell in row:
                cell_str = str(cell)
                if "," in cell_str or '"' in cell_str:
                    cell_str = '"' + cell_str.replace('"', '""') + '"'
                escaped.append(cell_str)
            lines.append(",".join(escaped))
        return "\n".join(lines)

    # unix format: tab-separated
    lines = []
    values = data.get("values", [])
    for row in values:
        lines.append("\t".join(str(cell) for cell in row))
    return "\n".join(lines)


# ============================================================================
# Phase 2: Data Manipulation & Formatting
# ============================================================================


def update_range_with_format(
    spreadsheet_id: str,
    range_spec: str,
    values: List[List[Any]],
    format_spec: Optional[Dict[str, Any]] = None,
    value_input_option: str = "USER_ENTERED",
) -> Dict[str, Any]:
    """Update range with optional formatting.

    Args:
        spreadsheet_id: Spreadsheet ID
        range_spec: A1 notation range
        values: 2D array of values
        format_spec: Optional formatting dict (bold, italic, color, etc.)
        value_input_option: "USER_ENTERED" or "RAW"

    Returns:
        Response dict
    """
    service = get_sheets_service()

    requests = []

    # Add values update
    requests.append(
        {
            "range": range_spec,
            "values": values,
            "majorDimension": "ROWS",
        }
    )

    # Add formatting if provided
    if format_spec:
        # This would use batchUpdate with UpdateCellsRequest
        # For now, just update values
        pass

    body = {"data": requests}

    try:
        result = (
            service.spreadsheets()
            .values()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
            .execute()
        )
        return result
    except HttpError as e:
        raise Exception(f"Error updating range {range_spec}: {e}")


# ============================================================================
# Phase 3: Sheet Structure & Advanced Features
# ============================================================================


def add_sheet(
    spreadsheet_id: str,
    sheet_name: str,
    rows: int = 1000,
    columns: int = 26,
) -> Dict[str, Any]:
    """Add a new sheet to spreadsheet.

    Args:
        spreadsheet_id: Spreadsheet ID
        sheet_name: Name for new sheet
        rows: Number of rows (default 1000)
        columns: Number of columns (default 26 = A-Z)

    Returns:
        Response dict with added sheet properties
    """
    service = get_sheets_service()

    body = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": sheet_name,
                        "gridProperties": {
                            "rowCount": rows,
                            "columnCount": columns,
                        },
                    }
                }
            }
        ]
    }

    try:
        result = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
            .execute()
        )
        return result
    except HttpError as e:
        raise Exception(f"Error adding sheet: {e}")


def delete_sheet(spreadsheet_id: str, sheet_id: int) -> Dict[str, Any]:
    """Delete a sheet from spreadsheet.

    Args:
        spreadsheet_id: Spreadsheet ID
        sheet_id: Sheet ID (numeric)

    Returns:
        Response dict
    """
    service = get_sheets_service()

    body = {"requests": [{"deleteSheet": {"sheetId": sheet_id}}]}

    try:
        result = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
            .execute()
        )
        return result
    except HttpError as e:
        raise Exception(f"Error deleting sheet: {e}")


def copy_sheet(
    spreadsheet_id: str,
    sheet_id: int,
    destination_spreadsheet_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Copy sheet to same or different spreadsheet.

    Args:
        spreadsheet_id: Source spreadsheet ID
        sheet_id: Sheet ID to copy
        destination_spreadsheet_id: Destination spreadsheet (defaults to same)

    Returns:
        Response dict with copied sheet info
    """
    service = get_sheets_service()

    body = {
        "requests": [
            {
                "copyPaste": {
                    "source": {
                        "sheetId": sheet_id,
                    },
                    "destination": {
                        "sheetId": sheet_id + 1,
                    },
                    "pasteType": "NORMAL",
                }
            }
        ]
    }

    try:
        result = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
            .execute()
        )
        return result
    except HttpError as e:
        raise Exception(f"Error copying sheet: {e}")


# ============================================================================
# Phase 4: Advanced Operations & Automation
# ============================================================================


def batch_update(
    spreadsheet_id: str, requests: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Execute multiple batch update requests.

    Args:
        spreadsheet_id: Spreadsheet ID
        requests: List of batch update request dicts

    Returns:
        Response dict with results
    """
    service = get_sheets_service()

    body = {"requests": requests}

    try:
        result = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
            .execute()
        )
        return result
    except HttpError as e:
        raise Exception(f"Error executing batch update: {e}")


def batch_update_from_file(
    spreadsheet_id: str, batch_file: str
) -> Dict[str, Any]:
    """Execute batch update from JSON file.

    Args:
        spreadsheet_id: Spreadsheet ID
        batch_file: Path to JSON file with requests

    Returns:
        Response dict
    """
    try:
        with open(batch_file) as f:
            batch_data = json.load(f)

        requests = batch_data.get("requests", [])
        return batch_update(spreadsheet_id, requests)
    except Exception as e:
        raise Exception(f"Error loading batch file: {e}")
