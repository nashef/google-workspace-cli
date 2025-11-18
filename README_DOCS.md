# Google Docs API Implementation Plan

## Overview

The Google Docs API v1 provides programmatic access to Google Docs documents for reading, creating, and modifying content. Unlike the Drive API which manages file storage and sharing, the Docs API focuses specifically on document content manipulation and automation.

**API Reference:** https://developers.google.com/workspace/docs/api/reference/rest/v1

**Key Difference from Drive API:**
- Drive API: File storage, organization, permissions, sharing, storage management
- Docs API: Document content, text manipulation, formatting, structure editing

## Core Resources

The Google Docs API consists of a single primary REST resource with focused operations:

### 1. **Documents** (Core operations)
- **create** - Creates a new blank document
- **get** - Retrieves document content and metadata
- **batchUpdate** - Applies multiple updates to a document atomically

## Document Structure

Understanding the document structure is key to the Docs API:

### Hierarchy
```
Document
├── Title (metadata)
├── Tabs (DocumentTab[])
│   └── Body
│       └── StructuralElements[]
│           ├── Paragraph
│           ├── Table
│           ├── TableOfContents
│           ├── SectionBreak
│           ├── HorizontalRule
│           └── Equation
└── Metadata
    ├── Revision History
    ├── Suggestions
    └── Named Ranges
```

### Content Elements

**StructuralElements:**
- **Paragraph** - Text container with formatting and styling
- **Table** - Grid of cells with content
- **TableOfContents** - Auto-generated TOC
- **SectionBreak** - Divides document into sections
- **HorizontalRule** - Visual divider
- **Equation** - Mathematical expressions

**Paragraph Elements (inside paragraphs):**
- **TextRun** - Contiguous text with uniform styling
- **InlineObject** - Images embedded in text
- **AutoText** - Auto-replaced content (page number, date, etc.)
- **PageBreak** - Page break
- **ColumnBreak** - Column break
- **Footnote/Endnote** - Reference notes

**Table Elements:**
- **TableRow** - Row in a table
- **TableCell** - Cell with content
- **Table of contents in cells**

## Batch Update Operations

The `batchUpdate` method applies multiple requests atomically. Major request types:

### Text Operations
- **InsertText** - Insert text at a location
- **DeleteContentRange** - Delete content between indices
- **ReplaceAllText** - Replace all occurrences of text
- **ReplaceNamedRangeContent** - Replace content in named ranges

### Formatting Operations
- **UpdateTextStyle** - Format text (bold, italic, font size, color, etc.)
- **UpdateParagraphStyle** - Format paragraphs (alignment, spacing, indentation)
- **UpdateTableCellStyle** - Format table cells

### Structural Operations
- **InsertTable** - Insert table at location
- **DeleteTable** - Remove table
- **InsertTableRow** - Add row to table
- **DeleteTableRow** - Remove row from table
- **InsertTableColumn** - Add column to table
- **DeleteTableColumn** - Remove column from table
- **InsertPageBreak** - Add page break
- **CreateParagraphBullets** - Convert paragraphs to list
- **CreateNamedRange** - Create named range
- **DeleteNamedRange** - Remove named range

### Image Operations
- **InsertInlineImage** - Embed image in document
- **DeleteInlineObject** - Remove embedded image
- **ReplaceImage** - Replace image content

### Advanced Operations
- **CreateFootnote** - Add footnote
- **DeleteFootnote** - Remove footnote
- **UpdateTableOfContents** - Refresh TOC
- **CreateHeader** - Add header section
- **CreateFooter** - Add footer section
- **DeleteHeader** - Remove header
- **DeleteFooter** - Remove footer

### Response Features
- **Replies** - Each update request can have a response
- **DocumentId** - Returned on create
- **Replies[].InsertText.text** - Confirmation of inserted text
- **Replies[].InsertTable.tableId** - ID of inserted table
- **Replies[].InsertInlineImage.objectId** - ID of inserted image

## Implementation Phases

### Phase 1: Core Document Operations
**Commands:** `gwc-docs create`, `get`, `read`

**Features:**
- Create new blank documents
- Get document metadata and full content
- Read document text content
- Parse and display document structure
- Export document content to text/JSON
- Display document statistics (word count, character count, etc.)

**Key Parameters:**
- `--title TEXT` - Document title
- `--output-file PATH` - Save document content
- `--format [text|json|markdown]` - Output format
- `--pretty` - Pretty-print JSON

**Use Cases:**
- Programmatic document creation from templates
- Export document content to other formats
- Analyze document structure
- Read document for processing

### Phase 2: Text Manipulation & Formatting
**Commands:** `gwc-docs insert-text`, `delete`, `replace`, `format-text`, `format-paragraph`

**Features:**
- Insert text at specific positions
- Delete content ranges
- Replace text (single or all occurrences)
- Format text (bold, italic, font, color, size)
- Format paragraphs (alignment, spacing, bullets)
- Apply heading styles
- Create and manage named ranges

**Key Parameters:**
- `--text TEXT` - Text to insert
- `--index INTEGER` - Position to insert/delete
- `--start-index INTEGER` - Start of range
- `--end-index INTEGER` - End of range
- `--find TEXT` - Text to find
- `--replace TEXT` - Replacement text
- `--font TEXT` - Font name
- `--size INTEGER` - Font size points
- `--bold` - Make bold
- `--italic` - Make italic
- `--color HEX` - Text color
- `--align [left|center|right|justify]` - Alignment
- `--name TEXT` - Named range name

**Use Cases:**
- Template variable substitution
- Bulk text updates
- Document formatting automation
- Creating styled documents programmatically

### Phase 3: Tables, Images & Advanced Structures
**Commands:** `gwc-docs insert-table`, `insert-image`, `create-header`, `create-footer`, `insert-page-break`, `insert-footnote`

**Features:**
- Insert and delete tables
- Manage table rows and columns
- Insert images from URLs or files
- Create headers and footers
- Add page breaks
- Insert footnotes and endnotes
- Create table of contents
- Manage sections

**Key Parameters:**
- `--rows INTEGER` - Number of rows
- `--columns INTEGER` - Number of columns
- `--image-url URL` - Image URL
- `--image-file PATH` - Local image file
- `--footnote TEXT` - Footnote text
- `--section-id INTEGER` - Section ID

**Use Cases:**
- Report generation with tables
- Document templating with images
- Creating styled business documents
- Adding navigation elements to documents

### Phase 4: Advanced Features & Automation
**Commands:** `gwc-docs batch-update`, `suggest`, `accept-suggestion`, `create-named-range`

**Features:**
- Apply multiple updates atomically
- Track and manage suggestions
- Accept/reject suggestions
- Work with named ranges
- Merge multiple documents
- Mail merge functionality
- Version tracking and comparison

**Key Parameters:**
- `--batch-file JSON` - JSON file with batch requests
- `--suggestion-id TEXT` - Suggestion ID
- `--accept` - Accept change
- `--reject` - Reject change
- `--revision INTEGER` - Revision ID

**Use Cases:**
- Complex document automation workflows
- Collaborative editing workflows
- Document generation pipelines
- Bulk document processing
- Multi-step document creation

## Batch Update Request Structure

The `batchUpdate` operation is central to the API. Basic structure:

```json
{
  "requests": [
    {
      "insertText": {
        "location": {
          "index": 1
        },
        "text": "Hello "
      }
    },
    {
      "updateTextStyle": {
        "range": {
          "startIndex": 1,
          "endIndex": 6
        },
        "textStyle": {
          "bold": true
        },
        "fields": "bold"
      }
    }
  ]
}
```

### Key Concepts

**Index System:**
- Zero-based indices refer to positions between characters
- Index 0 = before first character
- Index 1 = between first and second character
- Used for insertions and range selections
- Indices are in UTF-16 code units

**Range Objects:**
- **startIndex** - Inclusive start position
- **endIndex** - Exclusive end position
- Used for deletions, formatting, and selections

**Location Objects:**
- **index** - Position for insertion
- **tabId** - Which tab to edit (for multi-tab documents)

**Fields Masks:**
- Control which fields to update
- Prevents accidental overwrites
- Example: `"bold,italic,fontSize"`

## Comparison with Other APIs

| Feature | Docs API | Drive API | Sheets API |
|---------|----------|-----------|-----------|
| **Document Content** | Full | File metadata | Cells/ranges |
| **Read Operations** | Get full doc | File metadata | Read cells |
| **Write Operations** | Batch updates | Upload file | Update cells |
| **Formatting** | Text & paragraph | N/A | Cell format |
| **Tables** | Content tables | N/A | Native |
| **Images** | Embed inline | Store files | In cells |
| **Permissions** | Via Drive | Native | Via Drive |
| **Sharing** | Via Drive | Native | Via Drive |

## Output Formats

All commands support:
- `--output unix` - Tab-separated (default, for scripting)
- `--output json` - JSON (for programmatic parsing)
- `--output llm` - Human-readable (recommended for humans)

## Common Use Cases

### 1. Report Generation
```bash
gwc-docs create --title "Monthly Report"
gwc-docs insert-text doc_id --text "Executive Summary" --index 0
gwc-docs format-text doc_id --start-index 0 --end-index 18 --bold --size 14
gwc-docs insert-table doc_id --rows 5 --columns 3 --index 100
```

### 2. Document Templating
```bash
gwc-docs create --title "Customer Invoice {{date}}"
gwc-docs replace doc_id --find "{{customer}}" --replace "Acme Corp"
gwc-docs replace doc_id --find "{{amount}}" --replace "1500.00"
gwc-docs insert-image doc_id --image-file logo.png --index 50
```

### 3. Bulk Processing
```bash
gwc-docs batch-update doc_id --batch-file updates.json
```

### 4. Document Automation
```bash
gwc-docs create --title "Proposal"
# Insert sections with specific formatting
# Add tables with data
# Insert headers/footers
# Generate from data file
```

## API Limits & Considerations

1. **Rate Limits:**
   - 300 requests per minute per user
   - Batch operations count as single request (up to 100 requests per batch)

2. **Document Size:**
   - Documents limited to 50 MB when downloaded
   - Text content limited to 1 million characters

3. **Batch Update Atomicity:**
   - All requests in batch execute or all fail
   - Indices change based on earlier operations
   - Order matters in batch requests

4. **Indices:**
   - Zero-based system
   - UTF-16 code unit based (important for non-ASCII)
   - Insert/delete changes indices of later content

5. **Images:**
   - Supported formats: JPEG, PNG, GIF, BMP
   - Embedded images have size limits
   - Downloaded separately via Drive API

6. **Content Restrictions:**
   - Cannot directly edit suggestions mode
   - Headers/footers limited per section
   - Some formatting not accessible via API

## MIME Types

- Document: `application/vnd.google-apps.document`
- Docs uses the same MIME type as Drive storage

## Unique Aspects

**Complexity Factors:**
1. Index-based system requires careful position tracking
2. Batch operations need ordered requests
3. Index shifts with each operation
4. UTF-16 awareness needed for non-ASCII text

**Strengths:**
1. Atomic batch updates (all or nothing)
2. Atomic transactions across document
3. Powerful text processing capabilities
4. Good formatting support
5. Image embedding capability

**Limitations:**
1. No direct collaborative/suggestion editing via API
2. No spell check via API
3. Limited drawing/shapes support
4. No access to comments thread
5. Cannot directly edit revision history
