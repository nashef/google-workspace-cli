# Google Places API Implementation Plan

## Overview

The Google Places API provides programmatic access to Google's vast database of over 200 million places worldwide. It enables location-based search, place details retrieval, autocomplete functionality, and photo access for creating location-aware applications.

**API Reference:** https://developers.google.com/maps/documentation/places/web-service/overview

**API Key Required:** Yes (API key authentication; OAuth2 optional for certain operations)

**Status:** Phase 1-4 planned. Phases follow the Google Workspace CLI convention.

## Core Resources

The Google Places API consists of location-centric resources:

### 1. **Places Search** (Core Search Operations)
- **nearby_search** - Search for places within a specified radius
- **text_search** - Search for places using a text query
- **find_place** - Find specific places by input text
- **autocomplete** - Get place predictions from text input

### 2. **Places Details** (Detailed Information)
- **get_place** - Retrieve comprehensive details about a specific place
- **get_place_details** - Extended place information with reviews, hours, etc.

### 3. **Place Photos** (Media Access)
- **get_photo** - Retrieve a specific place photo by reference

### 4. **Session Tokens** (Cost Optimization)
- **create_session** - Create a session token for cost-optimized searches
- **session_operations** - Use tokens across multiple requests

## Place Structure

### Hierarchy
```
Place
├── PlaceID (unique identifier)
├── Location (lat/lng)
├── Name
├── Type (RESTAURANT, HOTEL, PARK, etc.)
├── Address
├── Contact Information
│   ├── Phone
│   ├── Website
│   └── Email
├── Hours & Schedule
│   ├── OpeningHours
│   ├── BusinessStatus
│   └── SpecialHours
├── Ratings & Reviews
│   ├── Rating (0-5)
│   ├── ReviewCount
│   └── Reviews[]
├── Photos[]
│   ├── PhotoReference
│   ├── Attribution
│   └── URL
├── Place Details
│   ├── FormattedAddress
│   ├── Geometry (lat/lng/viewport)
│   ├── PlusCode
│   ├── UTCOffset
│   ├── Vicinity
│   └── AccessibilityOptions
└── Metadata
    ├── PlaceType
    ├── Formatted Phone Number
    └── Permanently Closed
```

### Place Types

**Establishment Types:**
- RESTAURANT, CAFE, BAKERY, BAR, NIGHT_CLUB, LIQUOR_STORE
- HOTEL, MOTEL, APARTMENT_COMPLEX, LODGING
- MUSEUM, LIBRARY, MOVIE_THEATER, SHOPPING_MALL
- PHARMACY, HOSPITAL, DOCTOR, DENTAL_CLINIC, VETERINARY_CARE
- BANK, ACCOUNTING, FINANCE_SERVICE
- GAS_STATION, CAR_RENTAL, CAR_REPAIR, AUTO_PARTS_STORE
- PARK, GARDEN, ZOO, PLAYGROUND, CAMPGROUND
- SCHOOL, UNIVERSITY, COLLEGE
- GOVERNMENT_OFFICE, CITY_HALL, COURTHOUSE
- AIRPORT, TRAIN_STATION, BUS_STATION, FERRY_TERMINAL

**Address Types:**
- STREET_ADDRESS, ROUTE, INTERSECTION, POLITICAL (country, state, city, etc.)
- POSTAL_CODE, POSTAL_CODE_PREFIX

## Implementation Phases

### Phase 1: Core Search Operations (Planned)
**Commands:** `gwc-places search`, `text-search`, `find-place`, `autocomplete`

**Features:**
- Nearby search for places within specified radius
- Text-based place search
- Find place by input text
- Autocomplete place predictions
- Support for place types filtering
- Location bias (preferred area)
- Radius-based searches

**Key Parameters:**
- `--location LAT,LNG` - Center point for search
- `--radius INT` - Search radius in meters
- `--query TEXT` - Search query string
- `--input TEXT` - Input text for autocomplete/find
- `--type TEXT` - Filter by place type
- `--language CODE` - Language for results
- `--output [unix|json|llm]` - Output format

**Use Cases:**
- Restaurant/hotel discovery near user location
- Business/service location finder
- Address autocomplete in forms
- Location-based service discovery
- Nearby POI (Point of Interest) search

### Phase 2: Place Details & Photos (Planned)
**Commands:** `gwc-places get-place`, `get-details`, `get-photos`, `get-photo`

**Planned Features:**
- Retrieve comprehensive place information
- Access place photos and media
- Get opening hours and business status
- Access customer reviews and ratings
- Get contact information (phone, website)
- Retrieve accessibility information
- Place type and categorization

**Key Parameters:**
- `--place-id TEXT` - Place ID (from search results)
- `--fields TEXT` - Comma-separated fields to retrieve
- `--reviews BOOL` - Include customer reviews
- `--photos BOOL` - Include photos
- `--language CODE` - Language for reviews
- `--photo-index INT` - Index of photo to retrieve
- `--max-width INT` - Maximum photo width

**Use Cases:**
- Display place details in application
- Show business hours and contact info
- Display customer reviews
- Embed place photos in UI
- Retrieve accessibility information
- Business information aggregation

### Phase 3: Advanced Search Features (Planned)
**Commands:** `gwc-places search-advanced`, `search-along-route`, `session-create`, `session-end`

**Planned Features:**
- Price range filtering (budget to expensive)
- Open now filtering
- Rating filters (minimum rating)
- Business status (open/closed/permanently closed)
- Search along a route
- Session token management for cost optimization
- Diverse results (avoid clustering)

**Key Parameters:**
- `--min-price INT` - Minimum price level
- `--max-price INT` - Maximum price level
- `--open-now BOOL` - Filter to open places
- `--min-rating FLOAT` - Minimum rating filter
- `--route-points PATH` - Route for search-along-route
- `--session-token TEXT` - Session token for optimization
- `--diverse-results BOOL` - Return diverse results

**Use Cases:**
- Budget-conscious place searching
- Find open businesses right now
- Highly-rated venue discovery
- Route-based service discovery
- Cost-optimized search workflows

### Phase 4: Advanced Integration Features (Planned)
**Commands:** `gwc-places ai-summary`, `nearby-with-ranking`, `place-batch`, `export-places`

**Planned Features:**
- AI-powered place summaries
- Area-level AI summaries
- Ranking by relevance/popularity
- Batch place detail retrieval
- Export search results to multiple formats
- Caching strategies
- Search result aggregation

**Key Parameters:**
- `--summary-type TEXT` - Place, review, or area summary
- `--ranking TEXT` - Ranking method (relevance, popularity)
- `--place-ids FILE` - File with multiple place IDs
- `--export-format [json|csv|kml]` - Export format
- `--cache-duration INT` - Cache results for N seconds

**Use Cases:**
- Generate intelligent place descriptions
- Populate guidebooks with summaries
- Rank search results by relevance
- Batch process multiple places
- Integration with mapping applications
- Data export for external systems

## Search Types Comparison

| Feature | Text Search | Nearby Search | Find Place | Autocomplete |
|---------|------------|---------------|-----------|--------------|
| **Query Type** | Text query | Location + type | Specific text | Partial input |
| **Radius-based** | No | Yes | No | No |
| **Type Filtering** | Yes | Yes | Yes | Weak |
| **Price Range** | Yes | Yes | Yes | No |
| **Open Now** | Yes | Yes | Yes | No |
| **Rating Filter** | Yes | Yes | Yes | No |
| **Field Selection** | No | No | Yes | Limited |
| **Use Case** | General search | Nearby discovery | Exact matching | Form completion |

## Coordinate System

Places use standard geographic coordinates:

```
Latitude:  -90 to +90 (negative = South, positive = North)
Longitude: -180 to +180 (negative = West, positive = East)

Example: San Francisco
  Latitude:  37.7749
  Longitude: -122.4194

Search Radius: meters (1-50000)
```

## API Response Structure

### Search Result
```json
{
  "places": [
    {
      "name": "Restaurant Name",
      "placeId": "ChIJ...",
      "location": {
        "latitude": 37.7749,
        "longitude": -122.4194
      },
      "types": ["restaurant", "food"],
      "displayName": "Restaurant Name",
      "rating": 4.5,
      "businessStatus": "OPERATIONAL"
    }
  ],
  "nextPageToken": "token_for_next_page"
}
```

### Place Details
```json
{
  "name": "Restaurant Name",
  "placeId": "ChIJ...",
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "formattedAddress": "123 Main St, San Francisco, CA 94105",
  "types": ["restaurant", "food"],
  "rating": 4.5,
  "reviewCount": 245,
  "openingHours": {
    "openNow": true,
    "periods": [
      {
        "open": { "day": 0, "time": "1000" },
        "close": { "day": 0, "time": "2300" }
      }
    ],
    "weekdayText": ["Mon: 10:00 – 11:00 PM", ...]
  },
  "phoneNumber": "+1 (555) 123-4567",
  "website": "https://example.com",
  "photos": [
    {
      "name": "photos/ChIJ...",
      "heightPx": 400,
      "widthPx": 600,
      "authorAttributions": [
        {
          "displayName": "John Doe",
          "uri": "https://..."
        }
      ]
    }
  ]
}
```

## Output Formats

All commands support:
- `--output unix` - Tab-separated (default, for scripting)
- `--output json` - JSON (for programmatic parsing)
- `--output llm` - Human-readable (recommended for humans)
- `--output csv` - CSV (for spreadsheet import)
- `--output kml` - KML (for Google Earth/Maps import)

## Common Use Cases

### 1. Restaurant Discovery
```bash
# Search for nearby restaurants
gwc-places search --location 37.7749,-122.4194 --type RESTAURANT --radius 1000

# Filter by rating and price
gwc-places search-advanced --location 37.7749,-122.4194 \
  --type RESTAURANT --min-rating 4.0 --max-price 2

# Get details about specific restaurant
gwc-places get-place --place-id ChIJ...
```

### 2. Address Autocomplete
```bash
# Get place predictions as user types
gwc-places autocomplete --input "123 Main" --country US

# Get detailed address
gwc-places get-details --place-id ChIJ...
```

### 3. Hotel/Lodging Finder
```bash
# Find nearby hotels
gwc-places search --location 37.7749,-122.4194 --type HOTEL --radius 2000

# Filter by availability and ratings
gwc-places search-advanced --location 37.7749,-122.4194 \
  --type HOTEL --open-now --min-rating 4.5
```

### 4. Business Locator
```bash
# Text search for specific business
gwc-places text-search --query "Apple Store San Francisco"

# Get full business details
gwc-places get-details --place-id ChIJ...
```

### 5. Route-Based Service Discovery
```bash
# Find gas stations along route
gwc-places search-along-route --route-file route.geojson \
  --type GAS_STATION --radius 500
```

## API Limits & Considerations

### Rate Limits
- 300 requests per minute per API key
- Variable billing based on operation type:
  - Nearby Search: $6.50 per 1000 requests
  - Text Search: $6.50 per 1000 requests
  - Find Place: $6.50 per 1000 requests
  - Details: $6.50 per 1000 requests
  - Autocomplete: $3.50 per 1000 requests
  - Autocomplete Session: $0.00 (if using session tokens)

### Search Constraints
- Maximum radius: 50,000 meters (50 km)
- Minimum radius: 1 meter (practically 100+ meters)
- Results per page: up to 20
- Total results: pagination support via tokens
- Text query length: up to 2048 characters

### Data Consistency
- Place data updated in real-time
- Reviews updated continuously
- Photos added/removed by users
- Business hours may change seasonally
- No SLA for data completeness

### Image Limits
- Maximum 10 photos per place
- Photo dimensions: 400x600 to 1600x1200
- Supported formats: JPEG, WebP
- Photos must be attributed in UI

## Unique Aspects

**Strengths:**
1. Comprehensive place database (200M+ locations)
2. Real-time, crowd-sourced reviews and ratings
3. High-quality photos from users
4. Seamless Google Maps integration
5. Autocomplete for address entry
6. AI-powered summaries of places and areas
7. Search-along-route capability
8. Session token cost optimization
9. Flexible field selection (some endpoints)
10. Multiple language support

**Limitations:**
1. No historical place data (only current)
2. No real-time inventory/availability
3. No booking capability (integration only)
4. Photos require attribution display
5. Rate limiting per API key
6. Billing applies per request type
7. Some endpoints not available to all customers
8. Place updates can have delays
9. No offline capability
10. Search results quality varies by region

## Authentication & Scope

**API Key Authentication:**
- Simple API key in query string
- No scope management needed
- Suitable for server-side applications
- Billing tied to API key

**OAuth2 Authentication:**
- Required for user context
- Supports user-specific preferences
- Allows Drive integration for place list storage

**Scopes (if using OAuth2):**
```
https://www.googleapis.com/auth/geo
```

## MIME Types

- JSON Response: `application/json`
- Image/Photo: `image/jpeg`, `image/webp`
- KML Export: `application/vnd.google-earth.kml+xml`

## Implementation Roadmap

| Phase | Status | Effort | Features |
|-------|--------|--------|----------|
| 1 | 📋 Planned | Small | Search, text search, find, autocomplete |
| 2 | 📋 Planned | Medium | Place details, photos, reviews |
| 3 | 📋 Planned | Medium | Advanced filters, session tokens |
| 4 | 📋 Planned | Large | AI summaries, batch, export |

## Next Steps

1. **Phase 1**: Core search operations (nearby, text, find, autocomplete)
2. **Phase 2**: Place details and photos
3. **Phase 3**: Advanced search filters and session tokens
4. **Phase 4**: AI summaries, batch operations, export

## Key Differences from Other Google APIs

| Feature | Places | Workspace APIs | Maps API |
|---------|--------|----------------|----------|
| **Authentication** | API Key primary | OAuth2 primary | API Key primary |
| **Real-time Data** | Yes | No | Yes |
| **User Reviews** | Yes | Limited | No |
| **Geolocation** | Native | N/A | Native |
| **Search-focused** | Yes | No | No |
| **Billing Model** | Per-request | Per API limit | Per-request |
| **Rate Limits** | 300/min | Varies | 600/min |

---

**Note:** Places API implementation will follow the same patterns as other Google Workspace APIs (Calendar, Contacts, Docs, Drive, Email, Sheets, Slides) but uses API key authentication instead of OAuth2 exclusively.

**Next:** Review Google Places API documentation and plan implementation approach.
