---
name: sheets
description: Google Sheets spreadsheet operations, data manipulation, and analysis
---

# Sheets CLI Quick Reference

Base command: `poetry run gwc-sheets <command>`

## Quick Start

```bash
# Create a new spreadsheet
poetry run gwc-sheets create --title "Sales Report" --sheets "Data" --sheets "Analysis"

# Read data from a range
poetry run gwc-sheets read spreadsheet_id "A1:C10"

# Write data to a range
poetry run gwc-sheets update spreadsheet_id "A1:C3" --values '[[1,2,3],[4,5,6],[7,8,9]]'

# Append rows (auto-expanding)
poetry run gwc-sheets append spreadsheet_id "A:C" --values '[["new","row","data"]]'

# Get spreadsheet info
poetry run gwc-sheets get spreadsheet_id --output llm
```

## A1 Notation Guide

Cell and range references use standard A1 notation:

| Notation | Meaning |
|----------|---------|
| `A1` | Single cell |
| `A1:C10` | Range from A1 to C10 |
| `A:A` | Entire column A |
| `1:1` | Entire row 1 |
| `Sheet1!A1:C10` | Range on specific sheet |
| `'My Sheet'!A1:C10` | Sheet name with spaces |

## Spreadsheet Operations

| Task | Command |
|------|---------|
| Create spreadsheet | `create --title "Name" --sheets "Sheet1" --sheets "Sheet2"` |
| Get metadata | `get spreadsheet_id --output llm` |
| List sheets | `list-sheets spreadsheet_id --output llm` |
| Read range | `read spreadsheet_id "A1:C10"` |
| Read formatted | `read spreadsheet_id "A1:C10"` (default) |
| Read raw values | `read spreadsheet_id "A1:C10" --raw` |

## Data Manipulation

| Task | Command |
|------|---------|
| Write values | `update spreadsheet_id "A1:C3" --values '[[1,2,3],[4,5,6]]'` |
| Write formulas | `update spreadsheet_id "D1" --values '[["=SUM(A1:C1)"]]'` |
| Append rows | `append spreadsheet_id "A:C" --values '[["val1","val2","val3"]]'` |
| Clear range | `clear spreadsheet_id "A1:C10"` |
| Read multiple ranges | `batch-read spreadsheet_id "A1:C10" "Sheet2!A1:D5"` |

## Sheet Management

| Task | Command |
|------|---------|
| Add sheet | `add-sheet spreadsheet_id --sheet "NewSheet"` |
| Delete sheet | `delete-sheet spreadsheet_id --sheet-id 123456789` |
| List all sheets | `list-sheets spreadsheet_id --output json` |

## Output Formats

- `--output-format unix` - Tab-separated (default, for piping)
- `--output-format csv` - CSV export format
- `--output-format json` - Structured JSON data
- `--output llm` - Human-readable metadata

## Common Options

- `--values JSON` - 2D array of values: `'[["a","b"],["c","d"]]'`
- `--raw` - Show raw unformatted values
- `--output [unix|json|llm]` - Output format for metadata
- `--sheet NAME` - Sheet name for operations
- `--output-format [unix|csv|json]` - Data format for read operations

## Value Input Modes

When writing data:
- **USER_ENTERED** (default) - Formulas are interpreted (`=SUM(A1:C1)`)
- **RAW** (--raw flag) - Values stored literally (formulas as text)

## Data Format Examples

**Read as CSV**:
```bash
poetry run gwc-sheets read spreadsheet_id "A1:C100" --output-format csv
```

**Read as JSON**:
```bash
poetry run gwc-sheets read spreadsheet_id "A1:C10" --output-format json
```

**Write multiple rows**:
```bash
poetry run gwc-sheets update spreadsheet_id "A1:D10" \
  --values '[["Name","Age","City","Country"],["Alice",30,"NYC","USA"],["Bob",25,"LA","USA"]]'
```

**Append with formulas**:
```bash
poetry run gwc-sheets append spreadsheet_id "A:D" \
  --values '[["Total","","","=SUM(B:B)"]]'
```

## Batch Operations

For complex multi-step operations, use batch updates with JSON files:

```bash
poetry run gwc-sheets batch-update spreadsheet_id --batch-file updates.json
```

See the long-form documentation for batch file structure.

## Common Workflows

**Import CSV Data**:
```bash
# Convert CSV to JSON array
# Then use: poetry run gwc-sheets append id "A:Z" --values '[JSON_ARRAY]'
```

**Export to CSV**:
```bash
poetry run gwc-sheets read spreadsheet_id "A1:Z1000" --output-format csv > data.csv
```

**Create Report Template**:
```bash
# Create spreadsheet
ID=$(poetry run gwc-sheets create --title "Report" --output json | jq -r '.[0].id')

# Add headers
poetry run gwc-sheets update $ID "A1:D1" --values '[["Name","Value","Date","Status"]]'

# Add data
poetry run gwc-sheets append $ID "A:D" --values '[["Item1",100,"2024-01-01","Active"]]'
```

## Troubleshooting

**"No token found"** - Run `poetry run gwc auth` first

**"invalid_scope"** - Token missing Sheets permission, re-run `poetry run gwc auth`

**"Invalid range"** - Check A1 notation syntax (e.g., "A1:C10", not "A1-C10")

**Empty results** - Spreadsheet might be empty or range has no data

For more details, see: **SHEETS_QUICK_REFERENCE.md** and **README_SHEETS.md**
