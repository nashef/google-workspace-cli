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

## Coming in Phase 3+

- Insert tables and manage rows/columns
- Insert images from URLs or files
- Add headers, footers, page breaks
- Insert footnotes and endnotes
- Batch update operations
- Document manipulation and editing

## Documentation

- **README_DOCS.md** - Complete API overview and implementation plan
- **Phase 1** - Reading, analysis, and export operations
- **Phase 2** - Text insertion and formatting
- **Phase 3** - Tables, images, advanced structures
- **Phase 4** - Complex batch operations and automation
