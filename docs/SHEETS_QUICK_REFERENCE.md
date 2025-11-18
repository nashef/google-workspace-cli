# Google Sheets CLI - Quick Reference

## Installation & Setup

```bash
# Install CLI
poetry install

# Authenticate
poetry run gwc auth

# Verify installation
poetry run gwc-sheets --help
```

## Core Commands

### Create Spreadsheet
```bash
poetry run gwc-sheets create --title "My Spreadsheet"
poetry run gwc-sheets create --title "Report" --sheets "Data" --sheets "Analysis"
```

### Get Info
```bash
poetry run gwc-sheets get spreadsheet_id
poetry run gwc-sheets list-sheets spreadsheet_id
```

### Read Data
```bash
# Read range
poetry run gwc-sheets read spreadsheet_id "A1:C10"

# Read from specific sheet
poetry run gwc-sheets read spreadsheet_id "Sheet1!A1:D100"

# Read entire column
poetry run gwc-sheets read spreadsheet_id "A:A"

# Read with CSV output
poetry run gwc-sheets read spreadsheet_id "A1:C10" --output-format csv

# Read raw values (unformatted)
poetry run gwc-sheets read spreadsheet_id "A1:C10" --raw
```

### Write Data
```bash
# Write values
poetry run gwc-sheets update spreadsheet_id "A1:C3" --values '[[1,2,3],[4,5,6],[7,8,9]]'

# Write single cell
poetry run gwc-sheets update spreadsheet_id "A1" --values '[["Hello"]]'

# Write formulas (USER_ENTERED mode)
poetry run gwc-sheets update spreadsheet_id "D1" --values '[["=SUM(A1:C1)"]]'

# Write raw (formulas as text)
poetry run gwc-sheets update spreadsheet_id "A1" --values '[["=SUM(A1:C1)"]]' --raw
```

### Append Rows
```bash
# Append to sheet
poetry run gwc-sheets append spreadsheet_id "A:C" --values '[["row1","data","here"]]'

# Append multiple rows
poetry run gwc-sheets append spreadsheet_id "A:D" --values '[["a","b","c","d"],["e","f","g","h"]]'
```

### Clear Data
```bash
poetry run gwc-sheets clear spreadsheet_id "A1:C10"
poetry run gwc-sheets clear spreadsheet_id "Sheet1!A:Z"
```

### Sheet Management
```bash
# Add sheet
poetry run gwc-sheets add-sheet spreadsheet_id --sheet "NewSheet"

# Add sheet with custom size
poetry run gwc-sheets add-sheet spreadsheet_id --sheet "Data" --rows 5000 --columns 50

# Delete sheet (need sheet ID from list-sheets)
poetry run gwc-sheets delete-sheet spreadsheet_id --sheet-id 123456789
```

### Batch Operations
```bash
poetry run gwc-sheets batch-update spreadsheet_id --batch-file updates.json
```

## A1 Notation Guide

| Notation | Means |
|----------|-------|
| `A1` | Cell A1 |
| `A1:C10` | Range from A1 to C10 |
| `A:A` | Entire column A |
| `1:1` | Entire row 1 |
| `Sheet1!A1:C10` | Range on specific sheet |
| `'Sheet Name'!A1:C10` | Sheet name with spaces |

## Output Formats

```bash
# Unix (tab-separated) - default
poetry run gwc-sheets read spreadsheet_id "A1:C10" --output-format unix

# CSV
poetry run gwc-sheets read spreadsheet_id "A1:C10" --output-format csv

# JSON
poetry run gwc-sheets read spreadsheet_id "A1:C10" --output-format json

# Human-readable (for metadata)
poetry run gwc-sheets get spreadsheet_id --output llm
```

## Batch File Format

Create `updates.json`:
```json
{
  "requests": [
    {
      "addSheet": {
        "properties": {
          "title": "NewSheet",
          "gridProperties": {
            "rowCount": 1000,
            "columnCount": 26
          }
        }
      }
    },
    {
      "updateCells": {
        "range": {
          "sheetId": 0,
          "rowIndex": 0,
          "columnIndex": 0
        },
        "rows": [
          {
            "values": [
              {"userEnteredValue": {"stringValue": "Header"}}
            ]
          }
        ],
        "fields": "*"
      }
    }
  ]
}
```

Then execute:
```bash
poetry run gwc-sheets batch-update spreadsheet_id --batch-file updates.json
```

## Common Workflows

### Import CSV to Sheet
```bash
# Read CSV
cat data.csv | while IFS=',' read -r col1 col2 col3; do
  echo "[\"$col1\", \"$col2\", \"$col3\"]"
done

# Append to sheet (collect all rows first)
poetry run gwc-sheets append spreadsheet_id "A:C" --values '[["row1","data"],["row2","data"]]'
```

### Export Sheet to CSV
```bash
poetry run gwc-sheets read spreadsheet_id "A1:Z1000" --output-format csv > data.csv
```

### Copy Data Between Sheets
```bash
# Read from one sheet
poetry run gwc-sheets read spreadsheet_id "Sheet1!A1:C100" --output-format json > data.json

# Write to another sheet
poetry run gwc-sheets update spreadsheet_id "Sheet2!A1:C100" --values '...'
```

### Create Report Template
```bash
# Create spreadsheet
ID=$(poetry run gwc-sheets create --title "Report" --output json | jq -r '.[0].id')

# Add header
poetry run gwc-sheets update $ID "A1:D1" --values '[["Name","Value","Date","Status"]]'

# Add data
poetry run gwc-sheets append $ID "A:D" --values '[["Item1",100,"2024-01-01","Active"]]'

# View result
poetry run gwc-sheets read $ID "A:D"
```

## Scripting Tips

### Get Spreadsheet ID from Command Output
```bash
ID=$(poetry run gwc-sheets create --title "Test" --output json | jq -r '.[0].id')
echo "Created spreadsheet: $ID"
```

### Process CSV and Upload
```bash
# Convert CSV to JSON array format
python3 << 'EOF'
import csv
import json
import sys

rows = []
with open('data.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        rows.append(row)

print(json.dumps(rows))
EOF
```

### Read and Parse Output
```bash
# Read as JSON
poetry run gwc-sheets read spreadsheet_id "A1:C10" --output-format json | jq '.values[0]'

# Read as CSV and filter
poetry run gwc-sheets read spreadsheet_id "A1:C10" --output-format csv | grep "filter_term"
```

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| `No token found` | Not authenticated | Run `poetry run gwc auth` |
| `Invalid range` | Bad A1 notation | Check syntax (e.g., "A1:C10") |
| `Spreadsheet not found` | Invalid ID | Verify spreadsheet ID |
| `Permission denied` | Auth scope issue | Re-run `poetry run gwc auth` |
| `Invalid range name` | Sheet doesn't exist | Check sheet name/ID |

## Testing

```bash
# Run all Sheets tests
poetry run pytest tests/sheets/ -v

# Run specific test
poetry run pytest tests/sheets/test_operations.py::TestPhase1CoreOperations::test_read_range -v

# Run with coverage
poetry run pytest tests/sheets/ --cov=gwc.sheets

# Run integration tests only
poetry run pytest tests/sheets/test_integration.py -v
```

## API Limits

- **Rate limit**: 300 requests/minute per user
- **Batch size**: Up to 100 requests per batch operation
- **Cell content**: Max 50,000 characters per cell
- **Spreadsheet size**: 10 million cells per spreadsheet
- **Max rows**: 5 million rows

## Additional Resources

- **README_SHEETS.md** - Comprehensive API documentation
- **API Reference**: https://developers.google.com/workspace/sheets/api/reference/rest/v4
- **Python Quickstart**: https://developers.google.com/workspace/sheets/api/quickstart/python

---

Need help? Run `poetry run gwc-sheets COMMAND --help` for command-specific help.
