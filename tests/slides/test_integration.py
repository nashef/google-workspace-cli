"""Integration tests for Slides CLI.

These tests require valid Google Workspace credentials and API access.
Run with: pytest tests/slides/test_integration.py -v
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock


class TestSlidesIntegration:
    """Integration tests for Slides CLI commands."""

    @pytest.fixture
    def mock_slides_service(self):
        """Mock Slides API service."""
        with patch("gwc.slides.operations.get_slides_service") as mock:
            yield mock

    def test_end_to_end_presentation_workflow(self, mock_slides_service):
        """Test complete workflow: create, add slide, insert content."""
        from gwc.slides.operations import (
            create_presentation,
            add_slide,
            insert_text,
        )

        mock_service = Mock()
        mock_slides_service.return_value = mock_service

        # Create presentation
        mock_service.presentations().create().execute.return_value = {
            "presentationId": "test-pres-123"
        }

        pres_id = create_presentation("Sales Pitch")
        assert pres_id == "test-pres-123"

        # Add slide
        mock_service.presentations().get().execute.return_value = {
            "slides": [{"objectId": "slide-1", "layoutObjectId": "layout-1"}]
        }

        mock_service.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-pres-123",
            "replies": [{"addSlide": {"objectId": "slide-2"}}],
        }

        result = add_slide(pres_id)
        assert "presentationId" in result

        # Insert text
        mock_service.presentations().batchUpdate().execute.return_value = {
            "presentationId": "test-pres-123",
            "replies": [{"createShape": {"objectId": "textbox-1"}}],
        }

        text_result = insert_text(pres_id, "slide-2", "Welcome to Sales Pitch")
        assert "presentationId" in text_result

    def test_multiple_slides_workflow(self, mock_slides_service):
        """Test workflow with multiple slides and content."""
        from gwc.slides.operations import (
            create_presentation,
            add_slide,
            insert_text,
            insert_image,
            insert_shape,
            list_slides,
        )

        mock_service = Mock()
        mock_slides_service.return_value = mock_service

        # Create presentation
        mock_service.presentations().create().execute.return_value = {
            "presentationId": "test-pres-456"
        }

        pres_id = create_presentation("Multi-Slide Presentation")
        assert pres_id == "test-pres-456"

        # Get slides (for add_slide to work)
        mock_service.presentations().get().execute.return_value = {
            "slides": [
                {
                    "objectId": "slide-1",
                    "layoutObjectId": "layout-1",
                    "properties": {"name": "Title Slide"},
                }
            ]
        }

        # Add multiple slides
        for i in range(2, 4):
            mock_service.presentations().batchUpdate().execute.return_value = {
                "presentationId": pres_id,
                "replies": [{"addSlide": {"objectId": f"slide-{i}"}}],
            }
            add_slide(pres_id)

        # Insert different content types
        content_operations = [
            ("insert_text", insert_text, "test-pres-456", "slide-2", "Slide Title"),
            (
                "insert_image",
                insert_image,
                "test-pres-456",
                "slide-2",
                "https://example.com/image.png",
            ),
            (
                "insert_shape",
                insert_shape,
                "test-pres-456",
                "slide-3",
                "RECTANGLE",
            ),
        ]

        for op_name, op_func, *args in content_operations:
            mock_service.presentations().batchUpdate().execute.return_value = {
                "presentationId": pres_id,
                "replies": [{}],
            }
            result = op_func(*args)
            assert "presentationId" in result

        # List slides
        mock_service.presentations().get().execute.return_value = {
            "slides": [
                {
                    "objectId": f"slide-{i}",
                    "layoutObjectId": "layout-1",
                    "properties": {"name": f"Slide {i}"},
                }
                for i in range(1, 4)
            ]
        }

        slides = list_slides(pres_id)
        assert len(slides) == 3

    def test_slide_management_workflow(self, mock_slides_service):
        """Test slide management: add, duplicate, delete."""
        from gwc.slides.operations import (
            create_presentation,
            add_slide,
            duplicate_slide,
            delete_slide,
            list_slides,
        )

        mock_service = Mock()
        mock_slides_service.return_value = mock_service

        # Create
        mock_service.presentations().create().execute.return_value = {
            "presentationId": "test-pres-789"
        }

        pres_id = create_presentation("Slide Management Test")

        # Setup for add_slide
        mock_service.presentations().get().execute.return_value = {
            "slides": [{"objectId": "slide-1", "layoutObjectId": "layout-1"}]
        }

        # Add slide
        mock_service.presentations().batchUpdate().execute.return_value = {
            "presentationId": pres_id,
            "replies": [{"addSlide": {"objectId": "slide-2"}}],
        }

        add_slide(pres_id)

        # Duplicate slide
        mock_service.presentations().get().execute.return_value = {
            "slides": [
                {"objectId": "slide-1"},
                {"objectId": "slide-2"},
            ]
        }

        mock_service.presentations().batchUpdate().execute.return_value = {
            "presentationId": pres_id,
            "replies": [{"duplicateObject": {"objectId": "slide-2-copy"}}],
        }

        duplicate_slide(pres_id, "slide-2")

        # Delete slide
        mock_service.presentations().batchUpdate().execute.return_value = {
            "presentationId": pres_id,
            "replies": [{}],
        }

        delete_slide(pres_id, "slide-2")

        # List final slides
        mock_service.presentations().get().execute.return_value = {
            "slides": [
                {
                    "objectId": "slide-1",
                    "layoutObjectId": "layout-1",
                    "properties": {"name": "Slide 1"},
                },
                {
                    "objectId": "slide-2-copy",
                    "layoutObjectId": "layout-1",
                    "properties": {"name": "Slide 2"},
                },
            ]
        }

        slides = list_slides(pres_id)
        assert len(slides) == 2

    def test_batch_operations_workflow(self, mock_slides_service):
        """Test batch operations with multiple requests."""
        from gwc.slides.operations import (
            create_presentation,
            batch_update,
            batch_update_from_file,
        )

        mock_service = Mock()
        mock_slides_service.return_value = mock_service

        # Create
        mock_service.presentations().create().execute.return_value = {
            "presentationId": "test-pres-batch"
        }

        pres_id = create_presentation("Batch Operations Test")

        # Batch update with multiple requests
        requests = [
            {
                "addSlide": {
                    "objectId": "slide-2",
                }
            },
            {
                "createShape": {
                    "objectId": "text-1",
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": "slide-2",
                    },
                }
            },
        ]

        mock_service.presentations().batchUpdate().execute.return_value = {
            "presentationId": pres_id,
            "replies": [{}, {}],
        }

        result = batch_update(pres_id, requests)
        assert len(result["replies"]) == 2

        # Batch update from file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "requests": [
                        {
                            "updatePageProperties": {
                                "objectId": "slide-2",
                                "pageProperties": {"name": "Updated Slide"},
                                "fields": "name",
                            }
                        }
                    ]
                },
                f,
            )
            temp_file = f.name

        try:
            mock_service.presentations().batchUpdate().execute.return_value = {
                "presentationId": pres_id,
                "replies": [{}],
            }

            file_result = batch_update_from_file(pres_id, temp_file)
            assert "presentationId" in file_result
        finally:
            import os
            os.unlink(temp_file)

    def test_presentation_stats_workflow(self, mock_slides_service):
        """Test getting presentation statistics."""
        from gwc.slides.operations import (
            create_presentation,
            get_presentation_stats,
            add_slide,
            insert_text,
            insert_image,
            insert_shape,
        )

        mock_service = Mock()
        mock_slides_service.return_value = mock_service

        # Create
        mock_service.presentations().create().execute.return_value = {
            "presentationId": "test-pres-stats"
        }

        pres_id = create_presentation("Stats Test")

        # Add content
        mock_service.presentations().get().execute.return_value = {
            "slides": [{"objectId": "slide-1", "layoutObjectId": "layout-1"}]
        }

        mock_service.presentations().batchUpdate().execute.return_value = {
            "presentationId": pres_id,
            "replies": [{"addSlide": {"objectId": "slide-2"}}],
        }

        add_slide(pres_id)

        # Insert various content
        mock_service.presentations().batchUpdate().execute.return_value = {
            "presentationId": pres_id,
            "replies": [{"createShape": {}}],
        }

        insert_text(pres_id, "slide-2", "Title")
        insert_image(pres_id, "slide-2", "https://example.com/img.png")
        insert_shape(pres_id, "slide-2", "RECTANGLE")

        # Get stats
        mock_service.presentations().get().execute.return_value = {
            "title": "Stats Test",
            "presentationId": pres_id,
            "slides": [
                {
                    "properties": {"name": "Slide 1"},
                    "pageElements": [{"textBox": {}}],
                },
                {
                    "properties": {"name": "Slide 2"},
                    "pageElements": [
                        {"textBox": {}},
                        {"image": {}},
                        {"shape": {}},
                    ],
                },
            ],
        }

        stats = get_presentation_stats(pres_id)
        assert stats["slide_count"] == 2
        assert stats["total_text_boxes"] == 2
        assert stats["total_images"] == 1
        assert stats["total_shapes"] == 1

    def test_error_recovery_workflow(self, mock_slides_service):
        """Test error handling and recovery."""
        from gwc.slides.operations import (
            create_presentation,
            add_slide,
        )

        mock_service = Mock()
        mock_slides_service.return_value = mock_service

        # Create fails, then succeeds
        mock_service.presentations().create().execute.side_effect = [
            Exception("Temporary error"),
        ]

        with pytest.raises(Exception):
            create_presentation("Error Test")

        # Recovery: successful create on retry
        mock_service.presentations().create().execute.side_effect = None
        mock_service.presentations().create().execute.return_value = {
            "presentationId": "test-pres-error"
        }

        pres_id = create_presentation("Error Test Recovery")
        assert pres_id == "test-pres-error"


class TestSlidesCliIntegration:
    """Integration tests for CLI commands."""

    @patch("gwc.slides.operations.get_slides_service")
    def test_create_command_output(self, mock_slides_service):
        """Test create command output formatting."""
        from gwc.slides.operations import create_presentation

        mock_service = Mock()
        mock_slides_service.return_value = mock_service
        mock_service.presentations().create().execute.return_value = {
            "presentationId": "cli-test-123"
        }

        result = create_presentation("CLI Test")

        assert isinstance(result, str)
        assert result == "cli-test-123"

    @patch("gwc.slides.operations.get_slides_service")
    def test_list_slides_output_format(self, mock_slides_service):
        """Test list-slides command output format."""
        from gwc.slides.operations import list_slides

        mock_service = Mock()
        mock_slides_service.return_value = mock_service
        mock_service.presentations().get().execute.return_value = {
            "slides": [
                {
                    "objectId": "slide-1",
                    "layoutObjectId": "layout-1",
                    "properties": {"name": "Title"},
                },
                {
                    "objectId": "slide-2",
                    "layoutObjectId": "layout-1",
                    "properties": {"name": "Content"},
                },
            ]
        }

        result = list_slides("test-id")

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["index"] == 0
        assert result[0]["slide_id"] == "slide-1"
        assert "title" in result[0]

    @patch("gwc.slides.operations.get_slides_service")
    def test_get_command_output_format(self, mock_slides_service):
        """Test get command output format."""
        from gwc.slides.operations import get_presentation_stats

        mock_service = Mock()
        mock_slides_service.return_value = mock_service
        mock_service.presentations().get().execute.return_value = {
            "title": "Test Presentation",
            "presentationId": "test-id",
            "slides": [
                {
                    "properties": {"name": "Slide 1"},
                    "pageElements": [{"textBox": {}}],
                }
            ],
        }

        result = get_presentation_stats("test-id")

        assert isinstance(result, dict)
        assert "title" in result
        assert "slide_count" in result
        assert "total_text_boxes" in result
        assert result["title"] == "Test Presentation"
