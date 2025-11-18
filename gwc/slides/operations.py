"""Google Slides API operations.

Implements presentation read/write operations following the Slides API v1.
Supports spreadsheet-like operations for presentations.
"""

from typing import Any, List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
from pathlib import Path
from gwc.shared.auth import ALL_SCOPES

_slides_service = None


def get_slides_service():
    """Get or create Slides API service."""
    global _slides_service
    if _slides_service is None:
        creds = _load_credentials()
        _slides_service = build("slides", "v1", credentials=creds)
    return _slides_service


def _load_credentials() -> Credentials:
    """Load OAuth2 credentials from token file."""
    token_path = Path.home() / ".config" / "gwc" / "token.json"
    credentials_path = Path.home() / ".config" / "gwc" / "credentials.json"

    if not token_path.exists():
        raise Exception(
            "No token found. Run 'gwc auth' to authenticate first."
        )

    creds = Credentials.from_authorized_user_file(str(token_path), ALL_SCOPES)

    # Refresh if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed token
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())

    return creds


# ============================================================================
# Phase 1: Core Presentation Operations
# ============================================================================


def create_presentation(title: str) -> str:
    """Create a new blank presentation.

    Args:
        title: Presentation title

    Returns:
        Presentation ID
    """
    service = get_slides_service()

    body = {
        "title": title,
    }

    try:
        result = service.presentations().create(body=body).execute()
        return result["presentationId"]
    except HttpError as e:
        raise Exception(f"Error creating presentation: {e}")


def get_presentation(presentation_id: str) -> Dict[str, Any]:
    """Get presentation metadata and structure.

    Args:
        presentation_id: Presentation ID

    Returns:
        Presentation metadata dict
    """
    service = get_slides_service()

    try:
        result = service.presentations().get(presentationId=presentation_id).execute()
        return result
    except HttpError as e:
        raise Exception(f"Error getting presentation: {e}")


def get_presentation_title(presentation_id: str) -> str:
    """Get presentation title.

    Args:
        presentation_id: Presentation ID

    Returns:
        Presentation title
    """
    presentation = get_presentation(presentation_id)
    return presentation.get("title", "Untitled")


def list_slides(presentation_id: str) -> List[Dict[str, Any]]:
    """List all slides in presentation.

    Args:
        presentation_id: Presentation ID

    Returns:
        List of slide metadata dicts
    """
    presentation = get_presentation(presentation_id)
    slides = presentation.get("slides", [])

    result = []
    for i, slide in enumerate(slides):
        props = slide.get("properties", {})
        result.append(
            {
                "index": i,
                "slide_id": slide.get("objectId"),
                "title": props.get("name", f"Slide {i+1}"),
                "layout_id": slide.get("layoutObjectId"),
            }
        )

    return result


def get_presentation_stats(presentation_id: str) -> Dict[str, Any]:
    """Get presentation statistics.

    Args:
        presentation_id: Presentation ID

    Returns:
        Stats dict with slide count, etc.
    """
    presentation = get_presentation(presentation_id)
    slides = presentation.get("slides", [])

    # Count various element types
    total_text_boxes = 0
    total_images = 0
    total_shapes = 0

    for slide in slides:
        page_elements = slide.get("pageElements", [])
        for element in page_elements:
            if "textBox" in element:
                total_text_boxes += 1
            elif "image" in element:
                total_images += 1
            elif "shape" in element:
                total_shapes += 1

    return {
        "title": presentation.get("title", "Untitled"),
        "presentation_id": presentation_id,
        "slide_count": len(slides),
        "total_text_boxes": total_text_boxes,
        "total_images": total_images,
        "total_shapes": total_shapes,
        "slides": [
            {
                "index": i,
                "title": s.get("properties", {}).get("name", f"Slide {i+1}"),
                "elements": len(s.get("pageElements", [])),
            }
            for i, s in enumerate(slides)
        ],
    }


# ============================================================================
# Phase 2: Slide Management
# ============================================================================


def add_slide(
    presentation_id: str,
    slide_index: Optional[int] = None,
    layout_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a new slide to presentation.

    Args:
        presentation_id: Presentation ID
        slide_index: Position to insert (defaults to end)
        layout_id: Layout to use (defaults to blank)

    Returns:
        Response dict with added slide info
    """
    service = get_slides_service()

    # Get presentation to find layout ID if not provided
    presentation = get_presentation(presentation_id)
    slides = presentation.get("slides", [])

    # If no layout specified, use first available layout
    if layout_id is None and len(slides) > 0:
        layout_id = slides[0].get("layoutObjectId")

    # Build request
    request = {
        "addSlide": {
            "objectId": f"slide_{len(slides)+1}",
        }
    }

    if layout_id:
        request["addSlide"]["slideLayoutObjectId"] = layout_id

    if slide_index is not None:
        request["addSlide"]["insertionIndex"] = slide_index

    body = {"requests": [request]}

    try:
        result = service.presentations().batchUpdate(
            presentationId=presentation_id, body=body
        ).execute()
        return result
    except HttpError as e:
        raise Exception(f"Error adding slide: {e}")


def delete_slide(presentation_id: str, slide_id: str) -> Dict[str, Any]:
    """Delete a slide from presentation.

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID

    Returns:
        Response dict
    """
    service = get_slides_service()

    body = {
        "requests": [
            {
                "deleteObject": {
                    "objectId": slide_id,
                }
            }
        ]
    }

    try:
        result = service.presentations().batchUpdate(
            presentationId=presentation_id, body=body
        ).execute()
        return result
    except HttpError as e:
        raise Exception(f"Error deleting slide: {e}")


def duplicate_slide(
    presentation_id: str,
    slide_id: str,
    insert_after: bool = True,
) -> Dict[str, Any]:
    """Duplicate a slide.

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID to duplicate
        insert_after: Whether to insert after original (default) or before

    Returns:
        Response dict with duplicated slide info
    """
    service = get_slides_service()

    # Get slide index
    presentation = get_presentation(presentation_id)
    slides = presentation.get("slides", [])
    slide_index = None

    for i, slide in enumerate(slides):
        if slide.get("objectId") == slide_id:
            slide_index = i
            break

    if slide_index is None:
        raise Exception(f"Slide {slide_id} not found")

    # Build requests: create copy then update properties
    new_slide_id = f"slide_copy_{slide_index}"
    insert_index = slide_index + 1 if insert_after else slide_index

    body = {
        "requests": [
            {
                "duplicateObject": {
                    "objectId": slide_id,
                    "objectIds": {slide_id: new_slide_id},
                }
            }
        ]
    }

    try:
        result = service.presentations().batchUpdate(
            presentationId=presentation_id, body=body
        ).execute()
        return result
    except HttpError as e:
        raise Exception(f"Error duplicating slide: {e}")


# ============================================================================
# Phase 3: Content Operations
# ============================================================================


def insert_text(
    presentation_id: str,
    slide_id: str,
    text: str,
    x_position: int = 100000,
    y_position: int = 100000,
    width: int = 3000000,
    height: int = 500000,
) -> Dict[str, Any]:
    """Insert text box into slide.

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID
        text: Text content
        x_position: X position in EMU (default 100,000)
        y_position: Y position in EMU (default 100,000)
        width: Width in EMU (default 3,000,000 ≈ 3.3 inches)
        height: Height in EMU (default 500,000 ≈ 0.5 inches)

    Returns:
        Response dict
    """
    service = get_slides_service()

    text_box_id = f"textbox_{slide_id}_{len(text)}"

    body = {
        "requests": [
            {
                "createShape": {
                    "objectId": text_box_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": x_position,
                            "translateY": y_position,
                            "unit": "EMU",
                        },
                        "size": {
                            "width": {"magnitude": width, "unit": "EMU"},
                            "height": {"magnitude": height, "unit": "EMU"},
                        },
                    },
                    "text": {
                        "textElements": [
                            {
                                "textRun": {
                                    "content": text + "\n",
                                    "style": {},
                                }
                            }
                        ],
                        "lists": {},
                    },
                }
            }
        ]
    }

    try:
        result = service.presentations().batchUpdate(
            presentationId=presentation_id, body=body
        ).execute()
        return result
    except HttpError as e:
        raise Exception(f"Error inserting text: {e}")


def insert_image(
    presentation_id: str,
    slide_id: str,
    image_url: str,
    x_position: int = 100000,
    y_position: int = 100000,
    width: int = 2000000,
    height: int = 2000000,
) -> Dict[str, Any]:
    """Insert image into slide from URL.

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID
        image_url: URL of image to insert
        x_position: X position in EMU
        y_position: Y position in EMU
        width: Width in EMU
        height: Height in EMU

    Returns:
        Response dict
    """
    service = get_slides_service()

    image_id = f"image_{slide_id}_{len(image_url)}"

    body = {
        "requests": [
            {
                "createImage": {
                    "objectId": image_id,
                    "url": image_url,
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": x_position,
                            "translateY": y_position,
                            "unit": "EMU",
                        },
                        "size": {
                            "width": {"magnitude": width, "unit": "EMU"},
                            "height": {"magnitude": height, "unit": "EMU"},
                        },
                    },
                }
            }
        ]
    }

    try:
        result = service.presentations().batchUpdate(
            presentationId=presentation_id, body=body
        ).execute()
        return result
    except HttpError as e:
        raise Exception(f"Error inserting image: {e}")


def insert_shape(
    presentation_id: str,
    slide_id: str,
    shape_type: str,
    x_position: int = 100000,
    y_position: int = 100000,
    width: int = 1000000,
    height: int = 1000000,
) -> Dict[str, Any]:
    """Insert shape into slide.

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID
        shape_type: Shape type (RECTANGLE, ELLIPSE, TRIANGLE, etc.)
        x_position: X position in EMU
        y_position: Y position in EMU
        width: Width in EMU
        height: Height in EMU

    Returns:
        Response dict
    """
    service = get_slides_service()

    shape_id = f"shape_{slide_id}_{shape_type}"

    body = {
        "requests": [
            {
                "createShape": {
                    "objectId": shape_id,
                    "shapeType": shape_type,
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": x_position,
                            "translateY": y_position,
                            "unit": "EMU",
                        },
                        "size": {
                            "width": {"magnitude": width, "unit": "EMU"},
                            "height": {"magnitude": height, "unit": "EMU"},
                        },
                    },
                }
            }
        ]
    }

    try:
        result = service.presentations().batchUpdate(
            presentationId=presentation_id, body=body
        ).execute()
        return result
    except HttpError as e:
        raise Exception(f"Error inserting shape: {e}")


# ============================================================================
# Phase 4: Advanced Operations
# ============================================================================


def batch_update(
    presentation_id: str, requests: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Execute multiple batch update requests.

    Args:
        presentation_id: Presentation ID
        requests: List of update request dicts

    Returns:
        Response dict with results
    """
    service = get_slides_service()

    body = {"requests": requests}

    try:
        result = service.presentations().batchUpdate(
            presentationId=presentation_id, body=body
        ).execute()
        return result
    except HttpError as e:
        raise Exception(f"Error executing batch update: {e}")


def batch_update_from_file(
    presentation_id: str, batch_file: str
) -> Dict[str, Any]:
    """Execute batch update from JSON file.

    Args:
        presentation_id: Presentation ID
        batch_file: Path to JSON file with requests

    Returns:
        Response dict
    """
    try:
        with open(batch_file) as f:
            batch_data = json.load(f)

        requests = batch_data.get("requests", [])
        return batch_update(presentation_id, requests)
    except Exception as e:
        raise Exception(f"Error loading batch file: {e}")


def update_slide_properties(
    presentation_id: str,
    slide_id: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Update slide properties.

    Args:
        presentation_id: Presentation ID
        slide_id: Slide object ID
        name: New slide name

    Returns:
        Response dict
    """
    service = get_slides_service()

    body = {
        "requests": [
            {
                "updatePageProperties": {
                    "objectId": slide_id,
                    "pageProperties": {
                        "name": name,
                    },
                    "fields": "name",
                }
            }
        ]
    }

    try:
        result = service.presentations().batchUpdate(
            presentationId=presentation_id, body=body
        ).execute()
        return result
    except HttpError as e:
        raise Exception(f"Error updating slide properties: {e}")
