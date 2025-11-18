---
name: places
description: Google Places API location search, discovery, and place details
---

# Places CLI Quick Reference

Base command: `poetry run gwc-places <command>`

## Status

📋 **Places API implementation is planned.** This document outlines the upcoming CLI interface.

Full implementation will include:
- Phase 1: Nearby/text search, autocomplete
- Phase 2: Place details, photos, reviews
- Phase 3: Advanced filters, session tokens
- Phase 4: AI summaries, batch operations

## Quick Start (Planned)

```bash
# Search for nearby restaurants
poetry run gwc-places search --location 37.7749,-122.4194 --type RESTAURANT --radius 1000

# Find place by text
poetry run gwc-places text-search --query "Apple Store San Francisco"

# Get autocomplete predictions
poetry run gwc-places autocomplete --input "123 Main St"

# Get detailed place information
poetry run gwc-places get-place --place-id ChIJ... --output llm

# Get place photos
poetry run gwc-places get-photos --place-id ChIJ... --max-width 400
```

## Planned Operations

### Phase 1: Core Search (Planned)
- `search` - Search for places nearby (radius-based)
- `text-search` - Search by text query
- `find-place` - Find specific place by input
- `autocomplete` - Get place predictions from partial input

### Phase 2: Details & Media (Planned)
- `get-place` - Get comprehensive place details
- `get-details` - Extended place information
- `get-photos` - Retrieve place photos
- `get-photo` - Get specific photo reference

### Phase 3: Advanced Search (Planned)
- `search-advanced` - Search with filters (price, rating, open-now)
- `search-along-route` - Find places along a route
- `session-create` - Create cost-optimized session token
- `session-end` - End session token

### Phase 4: Advanced Integration (Planned)
- `ai-summary` - Get AI-generated place summary
- `nearby-with-ranking` - Search with relevance ranking
- `place-batch` - Batch retrieve place details
- `export-places` - Export search results

## Common Options

- `--location LAT,LNG` - Search center (latitude, longitude)
- `--radius INT` - Search radius in meters
- `--type TEXT` - Filter by place type (RESTAURANT, HOTEL, etc.)
- `--query TEXT` - Search query string
- `--input TEXT` - Input for autocomplete/find
- `--place-id TEXT` - Place ID from search results
- `--language CODE` - Language code (en, es, fr, etc.)
- `--output [unix|json|llm|csv|kml]` - Output format
- `--min-rating FLOAT` - Minimum rating filter
- `--max-price INT` - Maximum price level (1-4)
- `--open-now` - Only open businesses

## Place Types

**Common types for searching:**
- RESTAURANT, CAFE, BAKERY, BAR
- HOTEL, MOTEL, LODGING
- PHARMACY, HOSPITAL, DOCTOR
- BANK, ACCOUNTING
- GAS_STATION, CAR_RENTAL, AUTO_PARTS_STORE
- PARK, GARDEN, ZOO
- SCHOOL, UNIVERSITY
- MUSEUM, LIBRARY, THEATER
- AIRPORT, TRAIN_STATION

## Output Formats

- `--output unix` - Tab-separated (for scripting)
- `--output json` - Structured JSON data
- `--output csv` - CSV for spreadsheet import
- `--output llm` - Human-readable format
- `--output kml` - Google Earth/Maps compatible

## Search Result Examples

### Nearby Search Result
```
Name: Excellent Restaurant
PlaceID: ChIJ1234567890...
Location: 37.7749, -122.4194
Rating: 4.5 (245 reviews)
Type: RESTAURANT
Address: 123 Main St, San Francisco, CA
Status: OPERATIONAL
```

### Place Details
```
Name: Apple Store
PlaceID: ChIJ9876543210...
Phone: +1 (555) 123-4567
Website: https://apple.com
Address: 123 Market St, San Francisco, CA 94103
Hours: Mon-Sun 10:00 AM - 9:00 PM
Rating: 4.7 (891 reviews)
Photos: 15 available
```

## Common Workflows

### Restaurant Discovery
```bash
# Find nearby restaurants
gwc-places search \
  --location 37.7749,-122.4194 \
  --type RESTAURANT \
  --radius 2000 \
  --output llm

# Get restaurant details
gwc-places get-place \
  --place-id ChIJ... \
  --output json
```

### Address Autocomplete
```bash
# Get predictions as user types
gwc-places autocomplete \
  --input "123 Main" \
  --language en \
  --output json

# Get full details of selected place
gwc-places get-place --place-id ChIJ...
```

### Hotel Finder
```bash
# Find highly-rated hotels
gwc-places search-advanced \
  --location 37.7749,-122.4194 \
  --type HOTEL \
  --min-rating 4.5 \
  --open-now \
  --output csv
```

### Business Locator
```bash
# Text search for specific business
gwc-places text-search \
  --query "Starbucks San Francisco" \
  --language en

# Get full details
gwc-places get-place --place-id ChIJ... --output llm
```

## Authentication

**API Key Required:**
- Places API requires Google Maps API key (different from Workspace OAuth)
- Set via environment variable: `GOOGLE_PLACES_API_KEY`
- Or configure in `~/.config/gwc/places_config.json`

**Authentication Methods:**
1. API key in query string (automatic)
2. OAuth2 (when user context needed)

## API Limits & Billing

**Rate Limits:**
- 300 requests per minute per API key

**Pricing (as of 2024):**
- Nearby/Text/Find Search: $6.50 per 1,000 requests
- Place Details: $6.50 per 1,000 requests
- Autocomplete: $3.50 per 1,000 requests
- Autocomplete with Session: $0.00 (when using session tokens)
- Photos: $6.50 per 1,000 requests

**Cost Optimization:**
- Use session tokens for autocomplete workflows
- Request only needed fields
- Combine queries when possible

## Coordinate System

```
Latitude:  -90 to +90 (South to North)
Longitude: -180 to +180 (West to East)

Example: San Francisco
  37.7749, -122.4194

Search Radius: 1-50000 meters
```

## Troubleshooting

**"API key not configured"** - Set `GOOGLE_PLACES_API_KEY` environment variable

**"Invalid location format"** - Use format: `37.7749,-122.4194` (no spaces)

**"No results found"** - Try larger radius or remove filters

**"Rate limit exceeded"** - Wait and retry, or use session tokens

**"Invalid place ID"** - Place ID may be expired, search again

## Roadmap

| Phase | Target | Features |
|-------|--------|----------|
| 1 | 📋 Planned | Search, text-search, find, autocomplete |
| 2 | 📋 Planned | Place details, photos, reviews |
| 3 | 📋 Planned | Advanced filters, session tokens |
| 4 | 📋 Planned | AI summaries, batch, export |

## Key Differences from Workspace APIs

- Uses API key authentication (not OAuth2 primary)
- Real-time location data vs. document/calendar data
- Per-request billing model
- Geolocation-focused operations
- User reviews and ratings included

## Related Commands

```bash
# Combine with other CLIs for workflows
gwc-sheets append-range --sheet-id ID --values <search_results>
gwc-docs create --title "Places Report"
gwc-drive upload --parent-id ID --file results.csv
```

## Resources

- **README_PLACES.md** - Complete implementation plan and API reference
- **Google Places API Docs** - https://developers.google.com/maps/documentation/places/web-service
- **Place Types Reference** - https://developers.google.com/maps/documentation/places/web-service/supported_types

---

**Status**: Planning phase. Implementation to begin after Slides API completion.
