---
name: slides
description: Google Slides presentation creation and manipulation
---

# Slides CLI Quick Reference

Base command: `poetry run gwc-slides <command>`

## Status

⚠️ **Slides API implementation is in progress.** Currently supporting:
- Basic presentation creation
- Metadata retrieval

Full implementation (Phase 2-4) coming soon with:
- Slide management (add, delete, duplicate)
- Text and shape operations
- Image insertion
- Formatting and styling
- Master slide management
- Batch operations

## Quick Start

```bash
# Create a new presentation
poetry run gwc-slides create --title "My Presentation"

# Get presentation metadata
poetry run gwc-slides get presentation_id --output llm

# List slides in presentation
poetry run gwc-slides list-slides presentation_id
```

## Planned Operations

### Phase 1: Core (Implemented)
- `create` - Create new presentations
- `get` - Get metadata and properties
- `list-slides` - List all slides

### Phase 2: Slide Management (Coming)
- `add-slide` - Add new slides
- `delete-slide` - Remove slides
- `duplicate-slide` - Copy slides
- `reorder-slides` - Change slide order

### Phase 3: Content Operations (Coming)
- `insert-text` - Add text to slides
- `insert-image` - Add images
- `insert-shape` - Add shapes and objects
- `format-text` - Apply text formatting
- `update-layout` - Change slide layouts

### Phase 4: Advanced Features (Coming)
- `batch-update` - Complex multi-operation updates
- `apply-theme` - Apply themes and formatting
- `manage-master` - Master slide operations
- `export` - Export presentations

## Common Options

- `--output [unix|json|llm]` - Output format
- `--title TEXT` - Presentation title
- `--slide-id TEXT` - Specific slide ID
- `--batch-file PATH` - Batch operations file

## Presentation Properties

When created, presentations include:
- Title
- Slides (initially 1 blank slide)
- Layouts
- Master slides
- Themes

## Output Formats

- `--output unix` - Tab-separated (for scripting)
- `--output json` - Structured JSON data
- `--output llm` - Human-readable format

## Troubleshooting

**"No token found"** - Run `poetry run gwc auth` first

**"invalid_scope"** - Token missing Slides permission, re-run `poetry run gwc auth`

**API not responding** - Slides API requires proper OAuth scopes configured

## Roadmap

| Phase | Target | Features |
|-------|--------|----------|
| 1 | ✅ Done | Create, get, list slides |
| 2 | 🔄 Next | Slide management |
| 3 | 📋 Planned | Content insertion |
| 4 | 📋 Planned | Advanced features |

For more details as they become available, see: **README_SLIDES.md** (coming soon)

---

**Note**: The Slides API implementation is less urgent than spreadsheet/document work. Check back for updates as phases complete!
