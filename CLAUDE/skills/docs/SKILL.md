---
name: docs
description: Google Docs document manipulation, reading, and analysis
---

# Docs CLI Quick Reference

Base command: `poetry run gwc-docs <command>`

## Quick Start

```bash
# Create a new document
poetry run gwc-docs create --title "My Document"

# Get document metadata
poetry run gwc-docs get document_id --output llm

# Read document text
poetry run gwc-docs read document_id

# Export as different formats
poetry run gwc-docs export-text document_id --output-file output.txt
poetry run gwc-docs export-markdown document_id --output-file output.md
poetry run gwc-docs export-json document_id --output-file output.json
```

## Document Operations

| Task | Command |
|------|---------|
| Create document | `create --title "Document Name"` |
| Get metadata | `get document_id --output llm` |
| Get title only | `title document_id` |
| Read all text | `read document_id` |
| Get statistics | `stats document_id --output llm` |
| View structure | `structure document_id --output json` |

## Export & Download

| Task | Command |
|------|---------|
| Export as text | `export-text document_id --output-file output.txt` |
| Export as JSON | `export-json document_id --output-file output.json` |
| Export as Markdown | `export-markdown document_id --output-file output.md` |
| Display in stdout | `export-text document_id` |

## Common Options

- `--output [unix|json|llm]` - Output format for metadata
- `--title TEXT` - Document title for create
- `--output-file PATH` - Save export to file

## Statistics

The `stats` command returns:
- title - Document title
- document_id - The unique document ID
- character_count - Total characters in document
- word_count - Total words in document
- paragraph_count - Number of paragraphs
- table_count - Number of tables

## Document Structure

The `structure` command shows:
- Element types (paragraph, table, page_break, etc.)
- Paragraph styles (NORMAL_TEXT, HEADING_1, etc.)
- Table dimensions (rows x columns)
- Nesting and hierarchy

## Export Formats

**Text Export:**
- Plain text with newlines preserving structure
- Includes title as heading
- Tables shown with | separators
- Images noted as [Image]

**JSON Export:**
- Complete document object from API
- All metadata and content
- All structural information
- Good for programmatic processing

**Markdown Export:**
- Preserves headings (H1, H2, H3)
- Tables converted to Markdown format
- Images noted as [Image]
- Horizontal rules preserved
- Good for documentation workflows

## Common Use Cases

### 1. Document Analysis
```bash
gwc-docs stats document_id --output llm
gwc-docs structure document_id --output json
```

### 2. Content Extraction
```bash
gwc-docs read document_id > content.txt
gwc-docs export-text document_id --output-file document.txt
```

### 3. Format Conversion
```bash
gwc-docs export-markdown document_id --output-file document.md
gwc-docs export-json document_id --output-file document.json
```

### 4. Document Creation
```bash
gwc-docs create --title "New Report"
# Returns document ID for later use
```

## Tips

1. Use `export-markdown` to convert docs to docs-like markdown
2. Use `export-json` for programmatic document analysis
3. Use `read` to quickly view document content
4. Use `stats` to understand document composition
5. Use `structure` to see element types and organization
6. Export to file with `--output-file` for large documents

## Common Workflows

**Extract Document Content:**
```bash
DOC_ID="your-document-id"
gwc-docs read $DOC_ID > document.txt
```

**Backup Documents:**
```bash
gwc-docs export-json document_id --output-file backup.json
gwc-docs export-markdown document_id --output-file backup.md
```

**Document Inventory:**
```bash
gwc-docs stats document_id --output llm
```

**Convert for Publishing:**
```bash
gwc-docs export-markdown document_id --output-file README.md
```

## Phase 1 Capabilities

Phase 1 focuses on **reading and analyzing** documents:
- ✅ Create new documents
- ✅ Read document metadata
- ✅ Extract text content
- ✅ Analyze document statistics
- ✅ Export in multiple formats
- ✅ View document structure

## Phase 2: Text Manipulation & Formatting

Phase 2 enables **text editing and formatting**:
- ✅ Insert text at specific positions
- ✅ Delete text ranges
- ✅ Replace text (single or all occurrences)
- ✅ Format text (bold, italic, underline, strikethrough, color, font, size)
- ✅ Format paragraphs (alignment, spacing, heading styles)

### Phase 2 Commands

#### Text Insertion & Deletion

| Task | Command |
|------|---------|
| Insert text | `insert-text doc_id --text "Hello" --index 0` |
| Delete text | `delete doc_id --start-index 0 --end-index 5` |
| Replace text | `replace doc_id --find "old" --replace "new"` |

#### Character Formatting

| Option | Effect | Example |
|--------|--------|---------|
| `--bold` | Make text bold | `format-text doc_id --start-index 0 --end-index 5 --bold` |
| `--italic` | Make text italic | `format-text doc_id --start-index 0 --end-index 5 --italic` |
| `--underline` | Underline text | `format-text doc_id --start-index 0 --end-index 5 --underline` |
| `--strikethrough` | Strike through text | `format-text doc_id --start-index 0 --end-index 5 --strikethrough` |
| `--font TEXT` | Change font | `format-text doc_id --start-index 0 --end-index 5 --font "Arial"` |
| `--size INT` | Change size (points) | `format-text doc_id --start-index 0 --end-index 5 --size 14` |
| `--color HEX` | Change color | `format-text doc_id --start-index 0 --end-index 5 --color ff0000` |

#### Paragraph Formatting

| Option | Effect | Example |
|--------|--------|---------|
| `--align [left\|center\|right\|justify]` | Set alignment | `format-paragraph doc_id --start-index 0 --end-index 10 --align center` |
| `--indent INT` | Set indentation (points) | `format-paragraph doc_id --start-index 0 --end-index 10 --indent 36` |
| `--spacing-before INT` | Space before (points) | `format-paragraph doc_id --start-index 0 --end-index 10 --spacing-before 12` |
| `--spacing-after INT` | Space after (points) | `format-paragraph doc_id --start-index 0 --end-index 10 --spacing-after 12` |
| `--line-spacing FLOAT` | Line spacing multiplier | `format-paragraph doc_id --start-index 0 --end-index 10 --line-spacing 1.5` |
| `--heading STYLE` | Heading style | `format-paragraph doc_id --start-index 0 --end-index 10 --heading HEADING_1` |

Valid heading styles: `HEADING_1`, `HEADING_2`, `HEADING_3`, `HEADING_4`, `HEADING_5`, `HEADING_6`, `NORMAL_TEXT`

### Phase 2 Examples

**Template Variable Substitution:**
```bash
# Create from template
gwc-docs create --title "Invoice {{date}}"
DOC_ID="from_above"

# Replace placeholders
gwc-docs replace $DOC_ID --find "{{customer}}" --replace "Acme Corp"
gwc-docs replace $DOC_ID --find "{{amount}}" --replace "1500.00"
gwc-docs replace $DOC_ID --find "{{date}}" --replace "2025-11-18"
```

**Styled Document Creation:**
```bash
# Create document
DOC_ID=$(poetry run gwc-docs create --title "Report" | grep id | cut -d'"' -f4)

# Add and format title
gwc-docs insert-text $DOC_ID --text "Executive Summary" --index 0
gwc-docs format-text $DOC_ID --start-index 0 --end-index 18 --bold --size 16
gwc-docs format-paragraph $DOC_ID --start-index 0 --end-index 18 --heading HEADING_1 --align center

# Format body text
gwc-docs insert-text $DOC_ID --text "\n\nContent here." --index 18
gwc-docs format-paragraph $DOC_ID --start-index 19 --end-index 32 --line-spacing 1.5
```

**Bulk Text Updates:**
```bash
# Replace multiple instances
gwc-docs replace $DOC_ID --find "TODO" --replace "DONE"

# Format all instance (manual process)
gwc-docs format-text $DOC_ID --start-index 0 --end-index 100 --italic
```

### Phase 2 Important Notes

1. **Index System:**
   - Indices are 0-based (position 0 is before first character)
   - Use UTF-16 code unit positions
   - Delete/insert operations affect subsequent indices
   - Finding text position: use extracted text from `read` command

2. **Replace Behavior:**
   - Default: replaces ALL occurrences
   - Use `--replace-all` flag to control (default=true)
   - Use `--case-sensitive` for case matching (default=true)

3. **Formatting:**
   - Text formatting applies to character range
   - Paragraph formatting applies to all paragraphs in range
   - Multiple formatting options can be combined
   - Font names should match Google Docs fonts (Arial, Courier New, Georgia, etc.)

4. **Color Format:**
   - Use 6-digit hex without # (e.g., `ff0000` for red)
   - Format: `RRGGBB` where RR, GG, BB are hex values

5. **Atomic Batch Updates:**
   - Each operation is atomic (all or nothing)
   - Multiple operations in sequence may fail individually
   - For complex multi-step operations, consider Phase 4 batch updates

## Phase 3: Tables, Images & Advanced Structures

Phase 3 enables **structural elements** in documents:
- ✅ Insert tables with specified rows/columns
- ✅ Insert images from URLs
- ✅ Add page breaks
- ✅ Insert footnotes
- ✅ Create and delete headers/footers
- ✅ Manage document sections

### Phase 3 Commands

#### Table Operations

| Task | Command |
|------|---------|
| Insert table | `insert-table doc_id --rows 3 --columns 2 --index 0` |

#### Image Operations

| Task | Command |
|------|---------|
| Insert image from URL | `insert-image doc_id --image-url "https://..." --index 0` |

#### Structural Elements

| Task | Command |
|------|---------|
| Insert page break | `insert-page-break doc_id --index 50` |
| Insert footnote | `insert-footnote doc_id --text "Citation" --index 50` |
| Create header | `create-header doc_id` |
| Create header (section) | `create-header doc_id --section-id 1` |
| Create footer | `create-footer doc_id` |
| Create footer (section) | `create-footer doc_id --section-id 1` |
| Delete header | `delete-header doc_id header_id_here` |
| Delete footer | `delete-footer doc_id footer_id_here` |

### Phase 3 Examples

**Report with Tables:**
```bash
# Create document
DOC_ID=$(poetry run gwc-docs create --title "Sales Report" | grep id | cut -d'"' -f4)

# Add title
gwc-docs insert-text $DOC_ID --text "Q4 Sales Report" --index 0
gwc-docs format-text $DOC_ID --start-index 0 --end-index 15 --bold --size 16

# Add table
gwc-docs insert-table $DOC_ID --rows 4 --columns 3 --index 20
# Table structure: [Month | Q1 Sales | Q2 Sales | Q3 Sales | Q4 Sales]
#                  [Jan   | ...     | ...     | ...     | ...]
#                  [Feb   | ...     | ...     | ...     | ...]
#                  [Mar   | ...     | ...     | ...     | ...]

# Add page break for summary section
gwc-docs insert-page-break $DOC_ID --index 100

# Add footer
FOOTER_ID=$(poetry run gwc-docs create-footer $DOC_ID)
```

**Document with Headers/Footers:**
```bash
# Create main document
DOC_ID=$(poetry run gwc-docs create --title "Formal Report" | grep id | cut -d'"' -f4)

# Add content
gwc-docs insert-text $DOC_ID --text "Chapter 1: Introduction" --index 0

# Create header with page numbers
gwc-docs create-header $DOC_ID

# Create footer with copyright
gwc-docs create-footer $DOC_ID
```

**Document with Images:**
```bash
# Create document
DOC_ID=$(poetry run gwc-docs create --title "Product Presentation" | grep id | cut -d'"' -f4)

# Add title
gwc-docs insert-text $DOC_ID --text "Product Overview" --index 0
gwc-docs format-text $DOC_ID --start-index 0 --end-index 16 --bold --size 18

# Insert company logo
gwc-docs insert-image $DOC_ID --image-url "https://company.com/logo.png" --index 20

# Add text below image
gwc-docs insert-text $DOC_ID --text "\n\nProduct Features:" --index 21

# Add more images and content
gwc-docs insert-image $DOC_ID --image-url "https://company.com/feature1.png" --index 50
```

**Document with Footnotes:**
```bash
# Create document
DOC_ID=$(poetry run gwc-docs create --title "Academic Paper" | grep id | cut -d'"' -f4)

# Add text with citation placeholder
gwc-docs insert-text $DOC_ID --text "According to recent research " --index 0
gwc-docs insert-text $DOC_ID --text "[1] " --index 30

# Add footnote
gwc-docs insert-footnote $DOC_ID --text "Smith et al., 2024" --index 32
```

### Phase 3 Important Notes

1. **Table IDs:**
   - Tables return a `tableId` when inserted
   - Use this ID for future row/column operations
   - Store the ID for later manipulation (Phase 4)

2. **Image URLs:**
   - Only URLs work (no local files yet)
   - Must be publicly accessible
   - Returns `objectId` for tracking

3. **Headers/Footers:**
   - Each section can have its own header/footer
   - Default section ID is 0 (first section)
   - IDs returned can be used for deletion

4. **Footnotes:**
   - Automatically numbered by Google Docs
   - Can be endnotes or footnotes
   - Text is required parameter

5. **Page Structure:**
   - Document can have multiple sections
   - Each section supports headers/footers
   - Page breaks force content to new page

6. **Index Management:**
   - Plan indices carefully when combining operations
   - Index 0 = start of document
   - Each insertion shifts subsequent indices
   - Consider batching complex operations (Phase 4)

## Phase 4: Advanced Features & Automation

Phase 4 enables **complex workflows, templating, and automation**:
- ✅ Batch update operations (multiple changes atomically)
- ✅ Named ranges for templating and referencing
- ✅ Revision tracking information
- ✅ Support for multi-step document generation

### Phase 4 Commands

#### Batch Operations

| Task | Command |
|------|---------|
| Execute batch updates | `batch-update doc_id batch-requests.json` |

#### Named Ranges (Templating)

| Task | Command |
|------|---------|
| Create named range | `create-named-range doc_id --name "field" --start-index 0 --end-index 10` |
| Delete named range | `delete-named-range doc_id range_id_here` |

#### Revision History

| Task | Command |
|------|---------|
| Get revision info | `get-revisions doc_id` |

### Phase 4 Examples

**Batch Update with JSON File:**
```bash
# Create batch-requests.json
cat > batch-requests.json << 'JSON'
{
  "requests": [
    {
      "insertText": {
        "text": "Hello World",
        "location": {"index": 0}
      }
    },
    {
      "updateTextStyle": {
        "range": {"startIndex": 0, "endIndex": 11},
        "textStyle": {"bold": true},
        "fields": "bold"
      }
    },
    {
      "insertText": {
        "text": "\n\nSecond paragraph",
        "location": {"index": 11}
      }
    }
  ]
}
JSON

# Execute batch update
DOC_ID=$(poetry run gwc-docs create --title "Document" | grep id | cut -d'"' -f4)
gwc-docs batch-update $DOC_ID batch-requests.json
```

**Document Templating with Named Ranges:**
```bash
# Create template document
DOC_ID=$(poetry run gwc-docs create --title "Invoice" | grep id | cut -d'"' -f4)

# Add template text
gwc-docs insert-text $DOC_ID --text "Invoice To: [CUSTOMER_NAME]" --index 0
gwc-docs insert-text $DOC_ID --text "\nAmount: [AMOUNT]" --index 30
gwc-docs insert-text $DOC_ID --text "\nDate: [DATE]" --index 50

# Create named ranges for template fields
CUSTOMER_RANGE=$(poetry run gwc-docs create-named-range $DOC_ID --name "customer_name" --start-index 13 --end-index 27)
AMOUNT_RANGE=$(poetry run gwc-docs create-named-range $DOC_ID --name "amount" --start-index 40 --end-index 47)
DATE_RANGE=$(poetry run gwc-docs create-named-range $DOC_ID --name "date" --start-index 59 --end-index 63)

echo "Template created with ranges:"
echo "Customer: $CUSTOMER_RANGE"
echo "Amount: $AMOUNT_RANGE"
echo "Date: $DATE_RANGE"
```

**Mail Merge Simulation:**
```bash
# Create template
DOC_ID=$(poetry run gwc-docs create --title "Customer Letter" | grep id | cut -d'"' -f4)
gwc-docs insert-text $DOC_ID --text "Dear [CUSTOMER],\n\nThank you for your order of [PRODUCT] valued at [PRICE].\n\nBest regards,\nSales Team" --index 0

# Create named ranges for merge fields
gwc-docs create-named-range $DOC_ID --name "customer" --start-index 6 --end-index 16
gwc-docs create-named-range $DOC_ID --name "product" --start-index 50 --end-index 59
gwc-docs create-named-range $DOC_ID --name "price" --start-index 80 --end-index 85

# For actual data replacement, use batch updates or Sheets integration
```

**Complex Multi-Step Document Generation:**
```bash
# Create blank document
DOC_ID=$(poetry run gwc-docs create --title "Report" | grep id | cut -d'"' -f4)

# Define batch operations
cat > report-setup.json << 'JSON'
{
  "requests": [
    {
      "insertText": {
        "text": "Monthly Report - November 2025",
        "location": {"index": 0}
      }
    },
    {
      "updateTextStyle": {
        "range": {"startIndex": 0, "endIndex": 30},
        "textStyle": {"bold": true, "fontSize": {"magnitude": 16, "unit": "PT"}},
        "fields": "bold,fontSize"
      }
    },
    {
      "insertText": {
        "text": "\n\nExecutive Summary\n",
        "location": {"index": 30}
      }
    },
    {
      "updateParagraphStyle": {
        "range": {"startIndex": 33, "endIndex": 50},
        "paragraphStyle": {"namedStyleType": "HEADING_1"},
        "fields": "namedStyleType"
      }
    },
    {
      "insertPageBreak": {
        "location": {"index": 50}
      }
    },
    {
      "insertText": {
        "text": "Detailed Analysis",
        "location": {"index": 51}
      }
    }
  ]
}
JSON

# Execute all changes atomically
gwc-docs batch-update $DOC_ID report-setup.json
```

### Phase 4 Important Notes

1. **Batch Updates:**
   - All operations execute atomically (all succeed or all fail)
   - Requests are processed in order
   - Indices shift as each operation completes
   - Efficient for multi-step changes (single API call)
   - Up to 100 requests per batch

2. **Named Ranges:**
   - Must have unique names within document
   - Returns range ID for future reference
   - Useful for template placeholders
   - Can be deleted after use
   - Support mail-merge-like workflows

3. **Batch File Format:**
   - JSON file with "requests" array key
   - Each request is a batch operation object
   - Reference Google Docs API docs for operation types
   - Common operations: insertText, updateTextStyle, updateParagraphStyle

4. **Revision Tracking:**
   - `get-revisions` shows current revision info
   - Full revision history available via Drive API
   - Each document has a revision ID
   - Useful for tracking document versions

5. **Automation Patterns:**
   - Batch updates: Complex multi-step changes
   - Named ranges: Template variable placeholders
   - Combine with Sheets API for data-driven templates
   - Use for document generation pipelines

### Phase 4 Use Cases

- **Document Generation**: Build complex documents from templates with batch updates
- **Mail Merge**: Use named ranges + data source for bulk document creation
- **Report Automation**: Generate multi-page reports with consistent formatting
- **Template Processing**: Replace template variables in named ranges
- **Workflow Automation**: Complex multi-step document creation scripts

## Complete Docs API Coverage

All phases complete! You now have:
- **Phase 1** ✅ - Reading, analysis, export
- **Phase 2** ✅ - Text editing, formatting
- **Phase 3** ✅ - Tables, images, structural elements
- **Phase 4** ✅ - Batch operations, templating, automation

## Documentation

- **README_DOCS.md** - Complete API overview and implementation plan
- **Phase 1** - Reading, analysis, and export operations
- **Phase 2** - Text insertion and formatting
- **Phase 3** - Tables, images, advanced structures
- **Phase 4** - Complex batch operations and automation
