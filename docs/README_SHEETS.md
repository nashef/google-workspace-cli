# Google Sheets API Implementation Plan

## Overview

The Google Sheets API v4 provides programmatic access to Google Sheets spreadsheets for reading, creating, and modifying tabular data. Unlike the Drive API which manages file storage and sharing, the Sheets API focuses specifically on cell data manipulation, formatting, and spreadsheet automation.

**API Reference:** https://developers.google.com/workspace/sheets/api/reference/rest/v4

**Key Difference from Drive API:**
- Drive API: File storage, organization, permissions, sharing, storage management
- Sheets API: Cell data, ranges, formatting, calculations, sheet structure
- Docs API: Document content, text, tables, formatting
- Sheets API: Spreadsheet data, formulas, conditional formatting, pivot tables

## Core Resources

The Google Sheets API consists of four primary REST resources:

### 1. **Spreadsheets** (Core operations)
- **create** - Creates a new blank spreadsheet
- **get** - Retrieves spreadsheet metadata and structure
- **batchUpdate** - Applies multiple updates to spreadsheet structure

### 2. **Spreadsheets.Values** (Data manipulation - PRIMARY DATA RESOURCE)
- **get** - Reads cell values from a range
- **batchGet** - Reads multiple ranges in one request
- **batchGetByDataFilter** - Reads ranges matching data filters
- **update** - Writes values to a single range
- **batchUpdate** - Writes values to multiple ranges
- **append** - Appends values to end of range (auto-expands)
- **clear** - Removes values from a range
- **batchClear** - Clears multiple ranges
- **batchClearByDataFilter** - Clears ranges matching filters

### 3. **Spreadsheets.Sheets** (Sheet management)
- **copyTo** - Duplicates a sheet to same or different spreadsheet

### 4. **Spreadsheets.DeveloperMetadata** (Custom metadata)
- **get** - Retrieves metadata entry
- **search** - Finds metadata matching filters

## Spreadsheet Structure

Understanding spreadsheet structure is key to the Sheets API:

### Hierarchy
```
Spreadsheet
├── Metadata
│   ├── Title
│   ├── Locale
│   ├── Timezone
│   └── AutoRecalc settings
├── Sheets[]
│   ├── Title
│   ├── Sheet ID
│   ├── Grid Properties
│   │   ├── Row count
│   │   ├── Column count
│   │   ├── Frozen rows/columns
│   │   └── Hidden rows/columns
│   ├── Data (Values)
│   │   └── Cells (referenced by A1 notation: "A1", "B2:C10")
│   ├── Formatting
│   │   ├── Cell format (number format, borders, fill, font)
│   │   ├── Conditional formatting rules
│   │   └── Data validation rules
│   ├── Charts
│   ├── Protected ranges
│   └── Merged cells
├── Named Ranges (across entire spreadsheet)
└── Developer Metadata
```

### Data Notation

**A1 Notation** (standard spreadsheet notation):
- Single cell: `"A1"` (column A, row 1)
- Range: `"A1:C10"` (cells A1 to C10)
- Entire column: `"A:A"` (all of column A)
- Entire row: `"1:1"` (all of row 1)
- With sheet: `"Sheet1!A1:C10"` (range on specific sheet)
- Special syntax: `"A1:B" (rows/cols only)

**Grid Coordinates** (row/column indices):
- Row: 0-based index (0 = row 1)
- Column: 0-based index (0 = column A)
- Used in batchUpdate operations

## Data Types & Values

### Cell Value Types
- **String** - Text values
- **Number** - Numeric values (int, float)
- **Boolean** - true/false
- **Date** - Formatted as strings, formatted as dates by cell format
- **Error** - Formula errors (#DIV/0!, #N/A, etc.)
- **Formula** - Expressions starting with "=" (e.g., "=SUM(A1:A10)")

### Value Input Options
- **USER_ENTERED** - Input is treated as if user typed it (formulas interpreted)
- **RAW** - Input is stored exactly as provided (formulas become text)

### Value Render Options
- **FORMATTED_VALUE** - Values formatted per cell format rules
- **UNFORMATTED_VALUE** - Raw values without formatting
- **FORMULA** - Formulas (if cell contains formula)

### Date/Time Rendering
- **SERIAL_NUMBER** - Days since Dec 30, 1899
- **FORMATTED_STRING** - Formatted per locale/timezone

## Batch Update Operations

The `batchUpdate` method applies multiple requests atomically to spreadsheet structure. Major request types:

### Data Operations
- **UpdateValuesRequest** - Update cells in multiple ranges
- **AppendValuesRequest** - Append values to range

### Sheet Structure Operations
- **AddSheetRequest** - Create new sheet
- **DeleteSheetRequest** - Delete sheet
- **UpdateSheetPropertiesRequest** - Modify sheet properties (title, grid size, etc.)
- **InsertDimensionRequest** - Insert rows or columns
- **DeleteDimensionRequest** - Delete rows or columns
- **AppendDimensionRequest** - Expand rows or columns

### Formatting Operations
- **UpdateCellsRequest** - Format cells (border, fill, font, number format)
- **UpdateConditionalFormatRuleRequest** - Conditional formatting
- **UpdateDataValidationRequest** - Input validation rules
- **UpdateBordersRequest** - Cell borders
- **UpdateBooleanPropertiesRequest** - Boolean properties (merged cells, wrapped text, etc.)

### View Operations
- **UpdateSheetPropertiesRequest** - Sheet display properties (frozen rows/columns, etc.)
- **SetDataValidationRequest** - Data validation for ranges

### Protected Range Operations
- **AddProtectedRangeRequest** - Create protected range
- **UpdateProtectedRangeRequest** - Modify protection
- **DeleteProtectedRangeRequest** - Remove protection

### Named Range Operations
- **AddNamedRangeRequest** - Create named range
- **UpdateNamedRangeRequest** - Modify named range
- **DeleteNamedRangeRequest** - Remove named range

### Response Features
- **Replies** - Each update request can have a response
- **SpreadsheetId** - Returned on create
- **Replies[].AddSheet.properties** - New sheet details
- **UpdatedRows/Columns** - Count of affected cells

## Implementation Phases

### Phase 1: Core Spreadsheet Operations
**Commands:** `gwc-sheets create`, `get`, `list-sheets`, `read`

**Features:**
- Create new blank spreadsheets
- Get spreadsheet metadata and structure
- List all sheets in spreadsheet
- Read cell values from ranges
- Parse and display data
- Export to CSV/JSON
- Display spreadsheet statistics

**Key Parameters:**
- `--title TEXT` - Spreadsheet title
- `--sheet TEXT` - Sheet name (defaults to "Sheet1")
- `--range TEXT` - A1 notation range (e.g., "A1:C10")
- `--output-file PATH` - Save data
- `--format [csv|json|markdown]` - Output format

**Use Cases:**
- Programmatic data reading from sheets
- Export sheet data to other formats
- Analyze spreadsheet structure
- Automated data collection
- Report generation from sheet data

### Phase 2: Data Manipulation & Formatting
**Commands:** `gwc-sheets update`, `append`, `clear`, `format-cells`, `format-numbers`

**Features:**
- Update cell values in ranges
- Append rows to sheets (auto-expanding)
- Clear cell ranges
- Format cells (font, color, borders, fill)
- Format numbers (currency, percentage, date)
- Merge cells
- Set text wrapping and alignment
- Apply borders and styles

**Key Parameters:**
- `--range TEXT` - A1 notation range
- `--values JSON` - Values to insert (JSON array)
- `--formula TEXT` - Formula to insert
- `--font TEXT` - Font name
- `--size INTEGER` - Font size points
- `--bold` - Make bold
- `--italic` - Make italic
- `--color HEX` - Text color
- `--background HEX` - Fill color
- `--align [LEFT|CENTER|RIGHT]` - Horizontal alignment
- `--number-format TEXT` - Number format (e.g., "$#,##0.00")
- `--merge` - Merge cells in range

**Use Cases:**
- Automated data entry and updates
- Spreadsheet templating
- Bulk formatting operations
- Data import/migration
- Report generation with formatting

### Phase 3: Sheet Structure & Advanced Features
**Commands:** `gwc-sheets add-sheet`, `delete-sheet`, `insert-rows`, `insert-columns`, `add-named-range`, `delete-named-range`

**Features:**
- Add and delete sheets
- Insert/delete rows and columns
- Create named ranges (for formulas/references)
- Manage protected ranges
- Freeze rows/columns
- Hide/unhide rows and columns
- Set data validation rules
- Manage conditional formatting rules

**Key Parameters:**
- `--sheet TEXT` - Sheet name or ID
- `--index INTEGER` - Position to insert
- `--count INTEGER` - Number of rows/columns
- `--name TEXT` - Named range name
- `--locked` - Create protected/locked range
- `--criteria TEXT` - Validation criteria

**Use Cases:**
- Dynamic sheet creation from templates
- Automated row/column management
- Organizing complex spreadsheets
- Access control (protected ranges)
- Input validation (data validation rules)
- Conditional formatting rules

### Phase 4: Advanced Operations & Automation
**Commands:** `gwc-sheets batch-update`, `copy-sheet`, `search-metadata`, `apply-formulas`

**Features:**
- Execute complex multi-operation updates atomically
- Copy sheets within or between spreadsheets
- Work with developer metadata
- Apply formulas and calculated fields
- Handle data filters and complex queries
- Manage chart metadata
- Multi-step automation workflows

**Key Parameters:**
- `--batch-file JSON` - JSON file with batch requests
- `--destination-spreadsheet-id TEXT` - Target spreadsheet
- `--include-data` - Copy cell data when copying sheet
- `--metadata-key TEXT` - Custom metadata key
- `--metadata-value TEXT` - Custom metadata value

**Use Cases:**
- Complex spreadsheet automation workflows
- Multi-step data processing pipelines
- Spreadsheet cloning and templating
- Advanced reporting with calculations
- Cross-spreadsheet operations

## Range and Notation System

### A1 Notation Examples
```
"A1"                    # Single cell: Column A, Row 1
"A1:C10"                # Range: Columns A-C, Rows 1-10
"A:A"                   # Entire column A
"1:1"                   # Entire row 1
"A1:E"                  # Columns A to E, all rows
"1:100"                 # Rows 1 to 100, all columns
"Sheet1!A1:C10"         # Named sheet range
"'My Sheet'!A1:C10"     # Sheet name with spaces
```

### Important A1 Notation Rules
- Case-insensitive: "A1", "a1" are the same
- Column = letter(s), Row = number
- Range = start:end (inclusive on both sides)
- Sheet names with spaces need single quotes: `'Sheet Name'!A1`
- Unbounded: `"A:A"` = entire column A, `"1:1"` = entire row 1

### Grid Coordinates (for batchUpdate)
- Row: 0-based (0 = first row)
- Column: 0-based (0 = column A)
- Used in structured update requests
- Different from A1 notation (1-based)

## Comparison with Other APIs

| Feature | Sheets API | Drive API | Docs API |
|---------|-----------|-----------|----------|
| **Tabular Data** | Native | File metadata | Tables only |
| **Read Cells** | get/batchGet | File metadata | Text only |
| **Write Cells** | update/append | Upload file | batch updates |
| **Formulas** | Native | N/A | N/A |
| **Cell Formatting** | Native | N/A | Text/paragraph |
| **Calculations** | Automatic | N/A | N/A |
| **Validation Rules** | Native | N/A | N/A |
| **Permissions** | Via Drive | Native | Via Drive |
| **Sharing** | Via Drive | Native | Via Drive |

## Output Formats

All commands support:
- `--output unix` - Tab-separated (default, for scripting)
- `--output json` - JSON (for programmatic parsing)
- `--output llm` - Human-readable (recommended for humans)

## Common Use Cases

### 1. Data Import & Reporting
```bash
gwc-sheets read spreadsheet_id --range "A1:D100" --output csv > data.csv
gwc-sheets read spreadsheet_id --range "Sheet2!A1:C50" --output json | jq '.[]'
```

### 2. Automated Data Entry
```bash
gwc-sheets update spreadsheet_id --range "A1:C3" --values '[[1,2,3],[4,5,6],[7,8,9]]'
gwc-sheets append spreadsheet_id --range "A:C" --values '[["new","row","data"]]'
```

### 3. Report Generation with Formatting
```bash
gwc-sheets create --title "Monthly Report"
gwc-sheets update spreadsheet_id --range "A1" --values '[["Sales Data"]]'
gwc-sheets format-cells spreadsheet_id --range "A1" --bold --size 14
gwc-sheets format-numbers spreadsheet_id --range "B2:B100" --number-format "$#,##0.00"
```

### 4. Template-Based Processing
```bash
# Copy template sheet
gwc-sheets copy-sheet spreadsheet_id --sheet "Template" --destination-id new_spreadsheet_id
# Fill in data
gwc-sheets update spreadsheet_id --range "A2:C100" --values "[data]"
# Apply formatting and formulas
gwc-sheets batch-update spreadsheet_id --batch-file updates.json
```

### 5. Dynamic Sheet Management
```bash
gwc-sheets add-sheet spreadsheet_id --sheet "Week 1"
gwc-sheets add-sheet spreadsheet_id --sheet "Week 2"
gwc-sheets update spreadsheet_id --range "'Week 1'!A1:C10" --values "[weekly_data]"
```

## API Limits & Considerations

1. **Rate Limits:**
   - 300 requests per minute per user
   - Batch operations (up to 100 requests) count as one request
   - Read/write quotas: Varies by API pricing tier

2. **Data Size:**
   - Maximum cells per spreadsheet: 10 million
   - Maximum rows: 5 million (in 2024+)
   - Each cell can hold up to 50,000 characters

3. **Range Operations:**
   - Single range read/write up to 10 million cells (with restrictions)
   - A1 notation requests more efficient than grid coordinates
   - Batch operations maintain atomicity

4. **Batch Update Atomicity:**
   - All requests in batch execute or all fail
   - Indices change based on earlier operations
   - Order matters in batch requests
   - Up to 100 requests per batch

5. **Formatting:**
   - Cell format persists across value updates
   - Conditional formatting can impact performance on large ranges
   - Data validation applied per range

6. **Formulas:**
   - Must start with "=" when using USER_ENTERED mode
   - Calculation happens server-side (may be async)
   - RAW mode stores formula as text

7. **Protected Ranges:**
   - Applied per sheet
   - Can require editor permission
   - Protect content from accidental modification

## REST API Reference

This section documents the actual REST endpoints and structures used by the Sheets API v4.

### Spreadsheets Resource

#### Create Spreadsheet
```
POST /v4/spreadsheets
Request: {
  "properties": {
    "title": "string",
    "locale": "string",
    "timeZone": "string",
    "autoRecalc": "ON_CHANGE" | "ON_CHANGE" | "OFF"
  }
}
Response: Spreadsheet object with spreadsheetId, properties, sheets, etc.
```

#### Get Spreadsheet
```
GET /v4/spreadsheets/{spreadsheetId}
Response: Full Spreadsheet object with metadata, sheets, layouts, etc.
```

#### Batch Update Spreadsheet
```
POST /v4/spreadsheets/{spreadsheetId}:batchUpdate
Request: {
  "requests": [
    // Array of Request objects (AddSheetRequest, UpdateCellsRequest, etc.)
  ],
  "responseIncludes": ["SPREADSHEET_PROPERTIES", "SHEETS", "etc."]
}
Response: {
  "spreadsheetId": "string",
  "replies": [ /* responses from each request */ ]
}
```

#### Get by Data Filter
```
POST /v4/spreadsheets/{spreadsheetId}:getByDataFilter
Request: {
  "dataFilters": [ { "gridRange": {...} } or { "developerMetadataLookup": {...} } ]
}
Response: Data matching the filters
```

### Spreadsheets.Values Resource

#### Read Range
```
GET /v4/spreadsheets/{spreadsheetId}/values/{range}
Query Parameters:
  - valueRenderOption: "FORMATTED_VALUE" | "UNFORMATTED_VALUE" | "FORMULA"
  - dateTimeRenderOption: "SERIAL_NUMBER" | "FORMATTED_STRING"
Response: {
  "range": "string",
  "majorDimension": "ROWS" | "COLUMNS",
  "values": [ [ "cell1", "cell2" ], ... ]
}
```

#### Batch Get
```
POST /v4/spreadsheets/{spreadsheetId}/values:batchGet
Request: {
  "ranges": ["range1", "range2", ...],
  "valueRenderOption": "FORMATTED_VALUE",
  "dateTimeRenderOption": "FORMATTED_STRING"
}
Response: {
  "spreadsheetId": "string",
  "valueRanges": [ /* multiple ValueRange objects */ ]
}
```

#### Update Values
```
PUT /v4/spreadsheets/{spreadsheetId}/values/{range}
Query Parameters:
  - valueInputOption: "USER_ENTERED" | "RAW" (required)
Request: {
  "values": [ [ "val1", "val2" ], ... ],
  "majorDimension": "ROWS"
}
Response: {
  "updatedRange": "string",
  "updatedRows": integer,
  "updatedColumns": integer,
  "updatedCells": integer
}
```

#### Append Values
```
POST /v4/spreadsheets/{spreadsheetId}/values/{range}:append
Query Parameters:
  - valueInputOption: "USER_ENTERED" | "RAW"
  - insertDataOption: "OVERWRITE" | "INSERT_ROWS"
Request: {
  "values": [ [ "val1", "val2" ], ... ]
}
Response: {
  "spreadsheetId": "string",
  "updatedRange": "string",
  "updatedRows": integer,
  "updatedColumns": integer,
  "updatedCells": integer
}
```

#### Batch Update Values
```
POST /v4/spreadsheets/{spreadsheetId}/values:batchUpdate
Request: {
  "valueInputOption": "USER_ENTERED" | "RAW",
  "data": [
    {
      "range": "range1",
      "values": [ [ "val1", "val2" ], ... ]
    },
    // More ValueRange objects
  ]
}
Response: {
  "spreadsheetId": "string",
  "totalUpdatedRows": integer,
  "totalUpdatedColumns": integer,
  "totalUpdatedCells": integer,
  "responses": [ /* UpdateValuesResponse for each range */ ]
}
```

#### Clear Range
```
POST /v4/spreadsheets/{spreadsheetId}/values/{range}:clear
Response: {
  "spreadsheetId": "string",
  "clearedRange": "string"
}
```

#### Batch Clear Values
```
POST /v4/spreadsheets/{spreadsheetId}/values:batchClear
Request: {
  "ranges": ["range1", "range2", ...]
}
Response: {
  "spreadsheetId": "string",
  "clearedRanges": [ "range1", "range2", ... ]
}
```

### Spreadsheets.Sheets Resource

#### Copy Sheet
```
POST /v4/spreadsheets/{spreadsheetId}/sheets/{sheetId}:copyTo
Request: {
  "destinationSpreadsheetId": "spreadsheet_id" (optional - defaults to same spreadsheet)
}
Response: {
  "sheetId": integer,
  "title": "string",
  "index": integer,
  // ... other sheet properties
}
```

### Spreadsheets.DeveloperMetadata Resource

#### Get Metadata
```
GET /v4/spreadsheets/{spreadsheetId}/developerMetadata/{metadataId}
Response: DeveloperMetadata object
```

#### Search Metadata
```
POST /v4/spreadsheets/{spreadsheetId}/developerMetadata:search
Request: {
  "metadataFilter": {
    "metadataKey": "string",
    "metadataValue": "string",
    "visibility": "TEST_AND_NORMAL" | "TEST" | "NORMAL"
  }
}
Response: {
  "matchedMetadata": [ /* array of DeveloperMetadata */ ]
}
```

### Key Request Types for batchUpdate

The `batchUpdate` operation accepts many request types in the "requests" array:

**Sheet Management:**
- `AddSheetRequest` - Add new sheet
- `DeleteSheetRequest` - Remove sheet
- `UpdateSheetPropertiesRequest` - Modify sheet properties
- `InsertDimensionRequest` - Insert rows/columns
- `DeleteDimensionRequest` - Delete rows/columns
- `AppendDimensionRequest` - Expand grid

**Data Operations:**
- `UpdateValuesRequest` - Update cell values
- `UpdateCellsRequest` - Update cells with formatting

**Formatting:**
- `UpdateCellsRequest` - Cell formatting
- `UpdateConditionalFormatRuleRequest` - Conditional formatting
- `UpdateBordersRequest` - Cell borders
- `UpdateBooleanPropertiesRequest` - Text wrapping, merged cells

**Advanced:**
- `AddProtectedRangeRequest` - Create protected range
- `UpdateProtectedRangeRequest` - Modify protection
- `DeleteProtectedRangeRequest` - Remove protection
- `AddNamedRangeRequest` - Create named range
- `UpdateNamedRangeRequest` - Modify named range
- `DeleteNamedRangeRequest` - Remove named range

### Field Masks

When updating spreadsheet properties, use `fields` parameter to specify which fields to update:

```
fields: "properties.title,properties.locale,sheets(properties.title,data)"
```

Common field masks:
- `properties` - Spreadsheet properties (title, locale, timezone)
- `sheets` - Sheet list and their properties
- `namedRanges` - Named ranges
- `protectedRanges` - Protected ranges
- `developerMetadata` - Developer metadata

## MIME Types

- Spreadsheet: `application/vnd.google-apps.spreadsheet`
- CSV export: `text/csv`
- JSON export: `application/json`

## Unique Aspects

**Strengths:**
1. Native tabular data structure (unlike Docs or Drive)
2. Atomic batch updates (all or nothing)
3. Automatic calculations and formulas
4. Rich formatting options
5. Built-in data validation
6. Named ranges for formula references
7. A1 notation is universal and human-readable

**Complexity Factors:**
1. A1 notation learning curve initially
2. Grid coordinates vs A1 notation in different contexts
3. Value input/render options affect behavior
4. Batch operations require careful ordering
5. Large data operations need pagination

**Limitations:**
1. No built-in pivot table API (read-only access)
2. No charting API (read-only metadata)
3. No direct access to formula results vs raw values
4. Row/column insertion changes references
5. No comment API access
6. No real-time collaboration through API (events only)

## Next Steps

1. **Implement Phase 1**: Core read/write operations
2. **Add comprehensive testing** for A1 notation parsing
3. **Build Phase 2**: Formatting and styling
4. **Implement error handling** for common edge cases
5. **Document templates and workflows** for common scenarios
