"""Unit tests for Slides API operations."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from gwc.slides.operations import (
    create_presentation,
    get_presentation,
    get_presentation_title,
    list_slides,
    get_presentation_stats,
    add_slide,
    delete_slide,
    duplicate_slide,
    insert_text,
    insert_image,
    insert_shape,
    batch_update,
    batch_update_from_file,
    update_slide_properties,
)


class TestPhase1CoreOperations:
    """Test Phase 1: Core presentation operations."""

    @patch("gwc.slides.operations.get_slides_service")
    def test_create_presentation(self, mock_service):
        """Test creating a new presentation."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().create().execute.return_value = {
            "presentationId": "test-presentation-123"
        }

        result = create_presentation("Test Presentation")

        assert result == "test-presentation-123"
        # Verify the API was called
        assert mock_service_instance.presentations().create.call_count >= 1

    @patch("gwc.slides.operations.get_slides_service")
    def test_create_presentation_with_title(self, mock_service):
        """Test creating presentation with specific title."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().create().execute.return_value = {
            "presentationId": "test-id-456"
        }

        result = create_presentation("My Important Presentation")

        assert result == "test-id-456"

    @patch("gwc.slides.operations.get_slides_service")
    def test_get_presentation(self, mock_service):
        """Test getting presentation metadata."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().get().execute.return_value = {
            "presentationId": "test-id",
            "title": "My Presentation",
            "slides": [
                {
                    "objectId": "slide-1",
                    "properties": {"name": "Title Slide"},
                    "layoutObjectId": "layout-1",
                    "pageElements": [],
                }
            ],
        }

        result = get_presentation("test-id")

        assert result["presentationId"] == "test-id"
        assert result["title"] == "My Presentation"
        assert len(result["slides"]) == 1

    @patch("gwc.slides.operations.get_presentation")
    def test_get_presentation_title(self, mock_get):
        """Test getting presentation title."""
        mock_get.return_value = {"title": "Test Title"}

        result = get_presentation_title("test-id")

        assert result == "Test Title"

    @patch("gwc.slides.operations.get_presentation")
    def test_list_slides(self, mock_get):
        """Test listing slides in presentation."""
        mock_get.return_value = {
            "slides": [
                {
                    "objectId": "slide-1",
                    "properties": {"name": "Title Slide"},
                    "layoutObjectId": "layout-1",
                },
                {
                    "objectId": "slide-2",
                    "properties": {"name": "Content Slide"},
                    "layoutObjectId": "layout-1",
                },
            ]
        }

        result = list_slides("test-id")

        assert len(result) == 2
        assert result[0]["slide_id"] == "slide-1"
        assert result[0]["title"] == "Title Slide"
        assert result[1]["slide_id"] == "slide-2"

    @patch("gwc.slides.operations.get_presentation")
    def test_get_presentation_stats(self, mock_get):
        """Test getting presentation statistics."""
        mock_get.return_value = {
            "title": "Test Presentation",
            "presentationId": "test-id",
            "slides": [
                {
                    "properties": {"name": "Slide 1"},
                    "pageElements": [
                        {"textBox": {}},
                        {"image": {}},
                    ],
                },
                {
                    "properties": {"name": "Slide 2"},
                    "pageElements": [
                        {"shape": {}},
                    ],
                },
            ],
        }

        result = get_presentation_stats("test-id")

        assert result["title"] == "Test Presentation"
        assert result["presentation_id"] == "test-id"
        assert result["slide_count"] == 2
        assert result["total_text_boxes"] == 1
        assert result["total_images"] == 1
        assert result["total_shapes"] == 1


class TestPhase2SlideManagement:
    """Test Phase 2: Slide management operations."""

    @patch("gwc.slides.operations.get_slides_service")
    @patch("gwc.slides.operations.get_presentation")
    def test_add_slide(self, mock_get_pres, mock_service):
        """Test adding a new slide."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance

        mock_get_pres.return_value = {
            "slides": [
                {"objectId": "slide-1", "layoutObjectId": "layout-1"}
            ]
        }

        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{"addSlide": {"objectId": "slide-2"}}],
        }

        result = add_slide("test-id")

        assert "presentationId" in result
        # Verify the API was called
        assert mock_service_instance.presentations().batchUpdate.call_count >= 1

    @patch("gwc.slides.operations.get_slides_service")
    def test_delete_slide(self, mock_service):
        """Test deleting a slide."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{}],
        }

        result = delete_slide("test-id", "slide-1")

        assert "presentationId" in result
        # Verify the API was called
        assert mock_service_instance.presentations().batchUpdate.call_count >= 1

    @patch("gwc.slides.operations.get_slides_service")
    @patch("gwc.slides.operations.get_presentation")
    def test_duplicate_slide(self, mock_get_pres, mock_service):
        """Test duplicating a slide."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance

        mock_get_pres.return_value = {
            "slides": [
                {"objectId": "slide-1", "layoutObjectId": "layout-1"},
                {"objectId": "slide-2", "layoutObjectId": "layout-1"},
            ]
        }

        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{"duplicateObject": {"objectId": "slide-copy-1"}}],
        }

        result = duplicate_slide("test-id", "slide-1", insert_after=True)

        assert "presentationId" in result
        # Verify the API was called
        assert mock_service_instance.presentations().batchUpdate.call_count >= 1

    @patch("gwc.slides.operations.get_slides_service")
    @patch("gwc.slides.operations.get_presentation")
    def test_duplicate_slide_before(self, mock_get_pres, mock_service):
        """Test duplicating a slide before original."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance

        mock_get_pres.return_value = {
            "slides": [
                {"objectId": "slide-1"},
                {"objectId": "slide-2"},
            ]
        }

        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{"duplicateObject": {}}],
        }

        result = duplicate_slide("test-id", "slide-1", insert_after=False)

        assert "presentationId" in result


class TestPhase3ContentOperations:
    """Test Phase 3: Content operations."""

    @patch("gwc.slides.operations.get_slides_service")
    def test_insert_text(self, mock_service):
        """Test inserting text into slide."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{"createShape": {"objectId": "textbox-1"}}],
        }

        result = insert_text(
            "test-id", "slide-1", "Hello World", x_position=100000, y_position=100000
        )

        assert "presentationId" in result
        call_args = mock_service_instance.presentations().batchUpdate.call_args
        body = call_args[1]["body"]
        assert "requests" in body
        assert body["requests"][0]["createShape"]["shapeType"] == "TEXT_BOX"

    @patch("gwc.slides.operations.get_slides_service")
    def test_insert_text_with_dimensions(self, mock_service):
        """Test inserting text with custom dimensions."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{}],
        }

        result = insert_text(
            "test-id",
            "slide-1",
            "Title",
            x_position=500000,
            y_position=200000,
            width=2000000,
            height=1000000,
        )

        assert "presentationId" in result

    @patch("gwc.slides.operations.get_slides_service")
    def test_insert_image(self, mock_service):
        """Test inserting image into slide."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{"createImage": {"objectId": "image-1"}}],
        }

        url = "https://example.com/image.png"
        result = insert_image("test-id", "slide-1", url)

        assert "presentationId" in result
        call_args = mock_service_instance.presentations().batchUpdate.call_args
        body = call_args[1]["body"]
        assert body["requests"][0]["createImage"]["url"] == url

    @patch("gwc.slides.operations.get_slides_service")
    def test_insert_image_with_dimensions(self, mock_service):
        """Test inserting image with custom dimensions."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{}],
        }

        result = insert_image(
            "test-id",
            "slide-1",
            "https://example.com/img.jpg",
            x_position=300000,
            y_position=300000,
            width=1500000,
            height=1500000,
        )

        assert "presentationId" in result

    @patch("gwc.slides.operations.get_slides_service")
    def test_insert_shape(self, mock_service):
        """Test inserting shape into slide."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{"createShape": {"objectId": "shape-1"}}],
        }

        result = insert_shape("test-id", "slide-1", "RECTANGLE")

        assert "presentationId" in result
        call_args = mock_service_instance.presentations().batchUpdate.call_args
        body = call_args[1]["body"]
        assert body["requests"][0]["createShape"]["shapeType"] == "RECTANGLE"

    @patch("gwc.slides.operations.get_slides_service")
    def test_insert_different_shapes(self, mock_service):
        """Test inserting different shape types."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{}],
        }

        shapes = ["ELLIPSE", "TRIANGLE", "STAR", "HEART"]
        for shape_type in shapes:
            result = insert_shape("test-id", "slide-1", shape_type)
            assert "presentationId" in result


class TestPhase4AdvancedOperations:
    """Test Phase 4: Advanced operations."""

    @patch("gwc.slides.operations.get_slides_service")
    def test_batch_update(self, mock_service):
        """Test batch update with multiple requests."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{}, {}],
        }

        requests = [
            {"addSlide": {"objectId": "slide-2"}},
            {"insertText": {"objectId": "textbox-1"}},
        ]

        result = batch_update("test-id", requests)

        assert "presentationId" in result
        assert len(result["replies"]) == 2

    @patch("gwc.slides.operations.get_slides_service")
    def test_batch_update_from_file(self, mock_service):
        """Test batch update from JSON file."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{}],
        }

        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "requests": [
                        {"addSlide": {"objectId": "slide-2"}},
                    ]
                },
                f,
            )
            temp_file = f.name

        try:
            result = batch_update_from_file("test-id", temp_file)
            assert "presentationId" in result
        finally:
            import os
            os.unlink(temp_file)

    @patch("gwc.slides.operations.get_slides_service")
    def test_update_slide_properties(self, mock_service):
        """Test updating slide properties."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{}],
        }

        result = update_slide_properties("test-id", "slide-1", name="New Title")

        assert "presentationId" in result
        call_args = mock_service_instance.presentations().batchUpdate.call_args
        body = call_args[1]["body"]
        assert "updatePageProperties" in body["requests"][0]


class TestErrorHandling:
    """Test error handling."""

    @patch("gwc.slides.operations.get_slides_service")
    def test_create_presentation_error(self, mock_service):
        """Test error handling when creating presentation."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().create().execute.side_effect = Exception(
            "API Error"
        )

        with pytest.raises(Exception):
            create_presentation("Test")

    @patch("gwc.slides.operations.get_slides_service")
    def test_batch_update_error(self, mock_service):
        """Test error handling in batch update."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().batchUpdate().execute.side_effect = Exception(
            "Batch Update Failed"
        )

        with pytest.raises(Exception):
            batch_update("test-id", [{"addSlide": {}}])

    def test_batch_update_file_not_found(self):
        """Test error when batch file doesn't exist."""
        with pytest.raises(Exception):
            batch_update_from_file("test-id", "/nonexistent/file.json")


class TestEMUPositioning:
    """Test EMU (English Metric Units) positioning."""

    @patch("gwc.slides.operations.get_slides_service")
    def test_text_positioning_emu(self, mock_service):
        """Test that EMU positioning is correctly applied to text."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{}],
        }

        insert_text(
            "test-id",
            "slide-1",
            "Positioned Text",
            x_position=914400,  # 1 inch
            y_position=1828800,  # 2 inches
            width=2743200,  # 3 inches
            height=914400,  # 1 inch
        )

        call_args = mock_service_instance.presentations().batchUpdate.call_args
        body = call_args[1]["body"]
        transform = body["requests"][0]["createShape"]["elementProperties"]["transform"]

        assert transform["translateX"] == 914400
        assert transform["translateY"] == 1828800
        assert transform["unit"] == "EMU"

    @patch("gwc.slides.operations.get_slides_service")
    def test_image_positioning_emu(self, mock_service):
        """Test that EMU positioning is correctly applied to images."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-id",
            "replies": [{}],
        }

        insert_image(
            "test-id",
            "slide-1",
            "https://example.com/img.png",
            x_position=500000,
            y_position=500000,
            width=2000000,
            height=2000000,
        )

        call_args = mock_service_instance.presentations().batchUpdate.call_args
        body = call_args[1]["body"]
        transform = body["requests"][0]["createImage"]["elementProperties"]["transform"]

        assert transform["translateX"] == 500000
        assert transform["translateY"] == 500000
