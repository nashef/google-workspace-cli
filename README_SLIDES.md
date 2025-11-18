# Google Slides API Implementation Plan

## Overview

The Google Slides API v1 provides programmatic access to Google Slides presentations for creating, reading, and modifying slide content. Unlike the Docs API (text-focused) or Sheets API (data-focused), the Slides API handles visual presentation content including text, shapes, images, and slide layouts.

**API Reference:** https://developers.google.com/workspace/slides/api/reference/rest/v1

**Status:** Phase 1 (basic creation/reading) currently implemented. Phases 2-4 planned.

## Core Resources

The Google Slides API consists of presentation-centric resources:

### 1. **Presentations** (Core Operations)
- **create** - Creates new presentation
- **get** - Retrieves presentation metadata
- **batchUpdate** - Applies multiple updates

### 2. **Slides** (Slide Management)
- **get** - Retrieves slide details
- **batchUpdate** - Updates slide content

## Presentation Structure

### Hierarchy
```
Presentation
├── Title
├── Slides[]
│   ├── Layout (slide template)
│   ├── PageElements[]
│   │   ├── TextBox
│   │   │   └── TextRun (text with formatting)
│   │   ├── Image
│   │   ├── Shape
│   │   │   ├── Text
│   │   │   └── Fill
│   │   ├── Group
│   │   └── Table
│   └── BackgroundFill
├── Layouts[] (available slide templates)
├── Masters[] (master slides)
├── NotesMasters[] (notes templates)
└── Metadata
```

### Slide Elements
- **TextBox** - Contains text with formatting
- **Image** - Embedded images
- **Shape** - Predefined shapes (rectangle, circle, etc.)
- **Table** - Grid of cells
- **Group** - Container for multiple elements
- **Line** - Connectors and lines
- **Placeholder** - Template elements (title, subtitle, etc.)

## Implementation Phases

### Phase 1: Core Presentation Operations ✅
**Commands:** `gwc-slides create`, `get`, `list-slides`

**Features:**
- Create new presentations
- Retrieve presentation metadata
- List slides in presentation
- Get basic slide properties
- Support for slide layouts

**Key Parameters:**
- `--title TEXT` - Presentation title
- `--output [unix|json|llm]` - Output format

**Use Cases:**
- Programmatic presentation creation
- Metadata extraction
- Slide enumeration
- Template initialization

### Phase 2: Slide Management (Planned)
**Commands:** `gwc-slides add-slide`, `delete-slide`, `duplicate-slide`, `reorder-slides`

**Planned Features:**
- Add new slides to presentation
- Delete slides
- Duplicate existing slides
- Reorder slides
- Set slide layout
- Manage slide backgrounds

**Key Parameters:**
- `--slide-id TEXT` - Slide identifier
- `--layout TEXT` - Slide layout name
- `--position INTEGER` - Slide position
- `--background-color HEX` - Background color

**Use Cases:**
- Dynamic slide creation
- Slide management
- Template-based presentations
- Batch slide operations

### Phase 3: Content Operations (Planned)
**Commands:** `gwc-slides insert-text`, `insert-image`, `insert-shape`, `format-text`, `update-layout`

**Planned Features:**
- Add text boxes with formatting
- Insert images from URLs or files
- Add shapes and objects
- Apply text formatting (bold, italic, color, size)
- Update slide layouts
- Manage table content
- Position and size elements

**Key Parameters:**
- `--text TEXT` - Text content
- `--image-url URL` - Image URL
- `--image-file PATH` - Local image file
- `--font TEXT` - Font name
- `--size INTEGER` - Font size
- `--color HEX` - Text color
- `--shape TEXT` - Shape type

**Use Cases:**
- Automated report generation
- Presentation templating
- Content insertion
- Bulk text updates
- Image embedding

### Phase 4: Advanced Features (Planned)
**Commands:** `gwc-slides batch-update`, `apply-theme`, `manage-master`, `export`

**Planned Features:**
- Complex batch operations (atomic multi-step updates)
- Theme/style application
- Master slide management
- Speaker notes
- Embedded charts and formulas
- Presentation export
- Copy slides between presentations

**Key Parameters:**
- `--batch-file JSON` - Batch operations file
- `--theme TEXT` - Theme name
- `--export-format [pdf|pptx|png|jpeg]` - Export format
- `--notes TEXT` - Speaker notes

**Use Cases:**
- Complex presentation automation
- Batch reporting
- Master slide templates
- Presentation distribution
- Data-driven presentations

## Page Element Types

### Text Elements
- **TextBox** - Free-form text
- **Shape with text** - Text inside shapes
- **Placeholder** - Template text (title, body, etc.)

### Visual Elements
- **Image** - Raster images
- **Shape** - Rectangles, circles, lines, arrows
- **Table** - Data grids
- **Group** - Collections of elements
- **Line** - Connectors and decorative lines

### Slide-level Elements
- **Background** - Slide background fill
- **SpeakerNotes** - Notes for presenter
- **Thumbnail** - Slide preview

## Slide Layouts

Presentations include predefined layouts:
- **Title Slide** - Title and subtitle
- **Title and Content** - Title with bullet points
- **Title Only** - Just title
- **Blank** - Empty slide
- **Two Content** - Title with two columns
- **Comparison** - Side-by-side content
- Custom layouts (user-defined)

## Coordinate System

Elements use 1 inch = 914,400 EMU (English Metric Units):

```
Typical slide: 10 inches × 7.5 inches
In EMU: 9,144,000 × 6,858,000 EMU
Left: 0, Right: 9,144,000
Top: 0, Bottom: 6,858,000
```

## Text Formatting

Text can be formatted with:
- **Font** - Family, size, weight
- **Color** - RGB values
- **Style** - Bold, italic, underline, strikethrough
- **Alignment** - Left, center, right, justify
- **Spacing** - Line spacing, letter spacing
- **Effects** - Shadow, reflection, glow

## Comparison with Other APIs

| Feature | Slides | Docs | Sheets |
|---------|--------|------|--------|
| **Visual Design** | Native | Limited | N/A |
| **Text** | Yes | Native | Limited |
| **Tables** | Yes | Native | Native |
| **Images** | Native | Yes | Via cells |
| **Shapes** | Native | No | No |
| **Master Slides** | Native | Headers/footers | N/A |
| **Export** | PDF, PPTX, etc. | PDF, DOCX | CSV, XLSX |
| **Collaboration** | Via Drive | Native | Via Drive |

## Output Formats

All commands support:
- `--output unix` - Tab-separated (default, for scripting)
- `--output json` - JSON (for programmatic parsing)
- `--output llm` - Human-readable (recommended for humans)

## Common Use Cases

### 1. Generate Report Presentation
```bash
# Create presentation
gwc-slides create --title "Q4 Report"

# Add slides and content (Phase 3+)
# gwc-slides add-slide --layout "Title and Content"
# gwc-slides insert-text ...
# gwc-slides insert-image ...
```

### 2. Create from Template
```bash
# Clone existing presentation (Phase 4)
# Then update content with Phase 3 commands
```

### 3. Batch Generate Presentations
```bash
# Create multiple presentations from data
# Insert content from CSV/database
# Apply consistent formatting
```

## API Limits & Considerations

1. **Rate Limits:**
   - 300 requests per minute per user
   - Batch operations up to 100 requests per batch

2. **Presentation Size:**
   - Maximum 100 MB when downloaded
   - No strict limit on page count (performance may degrade)

3. **Element Limits:**
   - Practical limit ~10,000 elements per slide
   - Text limited to ~20,000 characters per text run

4. **Image Limits:**
   - Maximum 50 MB per image
   - Supported formats: JPEG, PNG, GIF, BMP, SVG, TIFF, WebP
   - Embedded images are copied (not referenced)

5. **Batch Updates:**
   - Atomic - all succeed or all fail
   - Element IDs change with insertions/deletions
   - Order matters

## Unique Aspects

**Strengths:**
1. Visual element support (shapes, images, etc.)
2. Slide layout templates
3. Master slide management
4. Speaker notes
5. Batch update atomicity
6. Export to multiple formats
7. Position/size precision

**Limitations:**
1. No collaborative editing via API (read-only suggestions)
2. No animation controls
3. Limited chart/graph support
4. No embedded video support
5. No custom shapes (only predefined)
6. Master slide editing limited

## MIME Types

- Presentation: `application/vnd.google-apps.presentation`
- Export as PDF: `application/pdf`
- Export as PPTX: `application/vnd.openxmlformats-officedocument.presentationml.presentation`

## Implementation Roadmap

| Phase | Status | Effort | Features |
|-------|--------|--------|----------|
| 1 | ✅ Done | Small | Create, get, list |
| 2 | 📋 Planned | Medium | Slide management |
| 3 | 📋 Planned | Large | Content operations |
| 4 | 📋 Planned | Large | Advanced features |

## Next Steps

1. **Phase 1**: Core operations ✅
2. **Phase 2**: Slide management (add, delete, reorder)
3. **Phase 3**: Content insertion (text, images, shapes)
4. **Phase 4**: Advanced features (themes, export, batch)

---

**Note:** Slides API implementation is lower priority than Sheets/Docs. Check back for progress updates.
