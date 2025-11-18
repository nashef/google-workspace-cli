---
name: docs
description: Google Docs document reading and analysis
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

## Coming in Phase 2+

- Insert and delete text
- Format text (bold, italic, color, size)
- Insert tables and manage rows/columns
- Insert images
- Add headers, footers, page breaks
- Batch update operations
- Document manipulation and editing

## Documentation

- **README_DOCS.md** - Complete API overview and implementation plan
- **Phase 1** - Reading, analysis, and export operations
- **Phase 2** - Text insertion and formatting
- **Phase 3** - Tables, images, advanced structures
- **Phase 4** - Complex batch operations and automation
