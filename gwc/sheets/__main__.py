"""Google Sheets CLI commands."""

import click
import json
from typing import Optional
from gwc.sheets.operations import (
    create_spreadsheet,
    get_spreadsheet,
    get_spreadsheet_title,
    list_sheets,
    read_range,
    read_ranges,
    write_range,
    append_range,
    clear_range,
    get_spreadsheet_stats,
    format_range_data,
    add_sheet,
    delete_sheet,
    copy_sheet,
    batch_update,
    batch_update_from_file,
)
from gwc.shared.output import format_output, OutputFormat


@click.group()
def main():
    """Google Sheets CLI (gwc-sheets)."""
    pass


# ============================================================================
# Phase 1: Core Spreadsheet Operations
# ============================================================================


@main.command()
@click.option("--title", default="Untitled Spreadsheet", help="Spreadsheet title")
@click.option(
    "--sheets",
    multiple=True,
    default=["Sheet1"],
    help="Sheet names (can specify multiple)",
)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def create_cmd(title, sheets, output):
    """Create a new blank spreadsheet.

    Examples:
        gwc-sheets create --title "My Spreadsheet"
        gwc-sheets create --title "Report" --sheets "Data" --sheets "Analysis"
        gwc-sheets create --title "Multi-sheet" --output json
    """
    try:
        sheet_list = list(sheets) if sheets else ["Sheet1"]
        spreadsheet_id = create_spreadsheet(title=title, sheets=sheet_list)
        result = {"id": spreadsheet_id, "title": title, "sheets": sheet_list}
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error creating spreadsheet: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("spreadsheet_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def get_cmd(spreadsheet_id, output):
    """Get spreadsheet metadata and stats.

    Examples:
        gwc-sheets get spreadsheet_id
        gwc-sheets get spreadsheet_id --output json
    """
    try:
        stats = get_spreadsheet_stats(spreadsheet_id)
        click.echo(format_output([stats], output))
    except Exception as e:
        click.echo(f"Error getting spreadsheet: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("spreadsheet_id")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def list_sheets_cmd(spreadsheet_id, output):
    """List all sheets in spreadsheet.

    Examples:
        gwc-sheets list-sheets spreadsheet_id
        gwc-sheets list-sheets spreadsheet_id --output json
    """
    try:
        sheets = list_sheets(spreadsheet_id)
        click.echo(format_output(sheets, output))
    except Exception as e:
        click.echo(f"Error listing sheets: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("spreadsheet_id")
@click.argument("range_spec")
@click.option(
    "--output-format",
    type=click.Choice(["unix", "json", "csv"]),
    default="unix",
    help="Output format for data",
)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format for metadata",
)
@click.option(
    "--raw",
    is_flag=True,
    help="Show raw unformatted values (default is formatted)",
)
def read_cmd(spreadsheet_id, range_spec, output_format, output, raw):
    """Read values from a range.

    Examples:
        gwc-sheets read spreadsheet_id "A1:C10"
        gwc-sheets read spreadsheet_id "Sheet1!A1:D100" --output-format csv
        gwc-sheets read spreadsheet_id "A:A" --raw
        gwc-sheets read spreadsheet_id "Sheet2!B1:B10" --output json
    """
    try:
        value_render = "UNFORMATTED_VALUE" if raw else "FORMATTED_VALUE"
        data = read_range(
            spreadsheet_id, range_spec, value_render_option=value_render
        )

        # Format data according to requested format
        formatted_data = format_range_data(data, output_format)
        click.echo(formatted_data)
    except Exception as e:
        click.echo(f"Error reading range {range_spec}: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("spreadsheet_id")
@click.argument("ranges", nargs=-1, required=True)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def batch_read_cmd(spreadsheet_id, ranges, output):
    """Read values from multiple ranges.

    Examples:
        gwc-sheets batch-read spreadsheet_id "A1:C10" "Sheet2!A1:D5"
        gwc-sheets batch-read spreadsheet_id "A:A" "B:B" "C:C" --output json
    """
    try:
        results = read_ranges(spreadsheet_id, list(ranges))
        # Format results for output
        for result in results:
            data = format_range_data(result, "unix")
            click.echo(data)
    except Exception as e:
        click.echo(f"Error reading ranges: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Phase 2: Data Manipulation & Formatting
# ============================================================================


@main.command()
@click.argument("spreadsheet_id")
@click.argument("range_spec")
@click.option(
    "--values",
    required=True,
    help="JSON array of values, or - for stdin (e.g., '[[1,2,3],[4,5,6]]')",
)
@click.option(
    "--raw",
    is_flag=True,
    help="Treat as raw values (formulas won't be interpreted)",
)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def update_cmd(spreadsheet_id, range_spec, values, raw, output):
    """Update values in a range.

    Examples:
        gwc-sheets update spreadsheet_id "A1:C3" --values '[[1,2,3],[4,5,6],[7,8,9]]'
        gwc-sheets update spreadsheet_id "A1" --values '[["Hello"]]'
        gwc-sheets update spreadsheet_id "B1:B5" --values '[[1],[2],[3],[4],[5]]'
    """
    try:
        # Parse values
        if values == "-":
            import sys
            values_json = sys.stdin.read()
        else:
            values_json = values

        values_data = json.loads(values_json)
        if not isinstance(values_data, list):
            raise ValueError("Values must be a JSON array of arrays")

        value_input_option = "RAW" if raw else "USER_ENTERED"
        result = write_range(
            spreadsheet_id,
            range_spec,
            values_data,
            value_input_option=value_input_option,
        )

        result_data = {
            "range": result.get("updatedRange"),
            "rows_updated": result.get("updatedRows"),
            "columns_updated": result.get("updatedColumns"),
            "cells_updated": result.get("updatedCells"),
        }
        click.echo(format_output([result_data], output))
    except Exception as e:
        click.echo(f"Error updating range {range_spec}: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("spreadsheet_id")
@click.argument("range_spec")
@click.option(
    "--values",
    required=True,
    help="JSON array of values to append (e.g., '[[1,2,3],[4,5,6]]')",
)
@click.option(
    "--raw",
    is_flag=True,
    help="Treat as raw values (formulas won't be interpreted)",
)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def append_cmd(spreadsheet_id, range_spec, values, raw, output):
    """Append values to end of range (auto-expands rows).

    Examples:
        gwc-sheets append spreadsheet_id "A:C" --values '[[1,2,3]]'
        gwc-sheets append spreadsheet_id "Sheet1!A:A" --values '[["row1"],["row2"]]'
    """
    try:
        values_data = json.loads(values)
        if not isinstance(values_data, list):
            raise ValueError("Values must be a JSON array of arrays")

        value_input_option = "RAW" if raw else "USER_ENTERED"
        result = append_range(
            spreadsheet_id,
            range_spec,
            values_data,
            value_input_option=value_input_option,
        )

        result_data = {
            "range": result.get("updates", {}).get("updatedRange"),
            "rows_appended": result.get("updates", {}).get("updatedRows"),
            "cells_appended": result.get("updates", {}).get("updatedCells"),
        }
        click.echo(format_output([result_data], output))
    except Exception as e:
        click.echo(f"Error appending to range {range_spec}: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("spreadsheet_id")
@click.argument("range_spec")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def clear_cmd(spreadsheet_id, range_spec, output):
    """Clear values from a range.

    Examples:
        gwc-sheets clear spreadsheet_id "A1:C10"
        gwc-sheets clear spreadsheet_id "Sheet1!A:Z"
    """
    try:
        result = clear_range(spreadsheet_id, range_spec)
        result_data = {
            "range": result.get("clearedRange"),
            "cells_cleared": len(result.get("clearedRange", "").split(":")),
        }
        click.echo(format_output([result_data], output))
    except Exception as e:
        click.echo(f"Error clearing range {range_spec}: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Phase 3: Sheet Structure & Advanced Features
# ============================================================================


@main.command()
@click.argument("spreadsheet_id")
@click.option("--sheet", required=True, help="New sheet name")
@click.option("--rows", type=int, default=1000, help="Number of rows (default 1000)")
@click.option("--columns", type=int, default=26, help="Number of columns (default 26)")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def add_sheet_cmd(spreadsheet_id, sheet, rows, columns, output):
    """Add a new sheet to spreadsheet.

    Examples:
        gwc-sheets add-sheet spreadsheet_id --sheet "Data"
        gwc-sheets add-sheet spreadsheet_id --sheet "Analysis" --rows 5000 --columns 50
    """
    try:
        result = add_sheet(spreadsheet_id, sheet_name=sheet, rows=rows, columns=columns)
        sheet_info = result["replies"][0]["addSheet"]["properties"]
        result_data = {
            "sheet_id": sheet_info.get("sheetId"),
            "title": sheet_info.get("title"),
            "rows": sheet_info.get("gridProperties", {}).get("rowCount"),
            "columns": sheet_info.get("gridProperties", {}).get("columnCount"),
        }
        click.echo(format_output([result_data], output))
    except Exception as e:
        click.echo(f"Error adding sheet: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("spreadsheet_id")
@click.option("--sheet-id", type=int, required=True, help="Sheet ID to delete")
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="unix",
    help="Output format",
)
def delete_sheet_cmd(spreadsheet_id, sheet_id, output):
    """Delete a sheet from spreadsheet.

    Examples:
        gwc-sheets delete-sheet spreadsheet_id --sheet-id 123456789
    """
    try:
        result = delete_sheet(spreadsheet_id, sheet_id)
        result_data = {"deleted_sheet_id": sheet_id, "success": True}
        click.echo(format_output([result_data], output))
    except Exception as e:
        click.echo(f"Error deleting sheet: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Phase 4: Advanced Operations & Automation
# ============================================================================


@main.command()
@click.argument("spreadsheet_id")
@click.option(
    "--batch-file",
    required=True,
    type=click.Path(exists=True),
    help="JSON file with batch requests",
)
@click.option(
    "--output",
    type=click.Choice(["unix", "json", "llm"]),
    default="json",
    help="Output format",
)
def batch_update_cmd(spreadsheet_id, batch_file, output):
    """Execute batch update from JSON file.

    Batch file format:
        {
          "requests": [
            {"updateCells": {...}},
            {"addSheet": {...}},
            ...
          ]
        }

    Examples:
        gwc-sheets batch-update spreadsheet_id --batch-file updates.json
        gwc-sheets batch-update spreadsheet_id --batch-file requests.json --output llm
    """
    try:
        result = batch_update_from_file(spreadsheet_id, batch_file)
        click.echo(format_output([result], output))
    except Exception as e:
        click.echo(f"Error executing batch update: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
