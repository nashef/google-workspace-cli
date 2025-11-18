"""Unit tests for Sheets API operations."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from gwc.sheets.operations import (
    create_spreadsheet,
    get_spreadsheet,
    get_spreadsheet_title,
    list_sheets,
    read_range,
    read_ranges,
    write_range,
    append_range,
    clear_range,
    get_spreadsheet_stats,
    format_range_data,
    add_sheet,
    delete_sheet,
    copy_sheet,
    batch_update,
    batch_update_from_file,
)


class TestPhase1CoreOperations:
    """Test Phase 1: Core spreadsheet operations."""

    @patch("gwc.sheets.operations.get_sheets_service")
    def test_create_spreadsheet(self, mock_service):
        """Test creating a new spreadsheet."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.spreadsheets().create().execute.return_value = {
            "spreadsheetId": "test-id-123"
        }

        result = create_spreadsheet("Test Spreadsheet", sheets=["Sheet1", "Sheet2"])

        assert result == "test-id-123"

    @patch("gwc.sheets.operations.get_sheets_service")
    def test_create_spreadsheet_default_sheets(self, mock_service):
        """Test creating spreadsheet with default sheets."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.spreadsheets().create().execute.return_value = {
            "spreadsheetId": "test-id-456"
        }

        result = create_spreadsheet("Another Spreadsheet")

        assert result == "test-id-456"

    @patch("gwc.sheets.operations.get_sheets_service")
    def test_get_spreadsheet(self, mock_service):
        """Test getting spreadsheet metadata."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.spreadsheets().get().execute.return_value = {
            "spreadsheetId": "test-id",
            "properties": {"title": "My Sheet"},
            "sheets": [{"properties": {"title": "Sheet1"}}],
        }

        result = get_spreadsheet("test-id")

        assert result["spreadsheetId"] == "test-id"
        assert result["properties"]["title"] == "My Sheet"

    @patch("gwc.sheets.operations.get_spreadsheet")
    def test_get_spreadsheet_title(self, mock_get):
        """Test getting spreadsheet title."""
        mock_get.return_value = {"properties": {"title": "Test Title"}}

        result = get_spreadsheet_title("test-id")

        assert result == "Test Title"

    @patch("gwc.sheets.operations.get_spreadsheet")
    def test_list_sheets(self, mock_get):
        """Test listing sheets."""
        mock_get.return_value = {
            "sheets": [
                {
                    "properties": {
                        "sheetId": 0,
                        "title": "Sheet1",
                        "gridProperties": {"rowCount": 1000, "columnCount": 26},
                    }
                },
                {
                    "properties": {
                        "sheetId": 1,
                        "title": "Sheet2",
                        "gridProperties": {"rowCount": 500, "columnCount": 10},
                    }
                },
            ]
        }

        result = list_sheets("test-id")

        assert len(result) == 2
        assert result[0]["title"] == "Sheet1"
        assert result[1]["title"] == "Sheet2"

    @patch("gwc.sheets.operations.get_sheets_service")
    def test_read_range(self, mock_service):
        """Test reading a range."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.spreadsheets().values().get().execute.return_value = {
            "range": "Sheet1!A1:C3",
            "majorDimension": "ROWS",
            "values": [["A1", "B1", "C1"], ["A2", "B2", "C2"], ["A3", "B3", "C3"]],
        }

        result = read_range("test-id", "A1:C3")

        assert result["range"] == "Sheet1!A1:C3"
        assert len(result["values"]) == 3

    @patch("gwc.sheets.operations.get_sheets_service")
    def test_read_ranges(self, mock_service):
        """Test reading multiple ranges."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.spreadsheets().values().batchGet().execute.return_value = {
            "valueRanges": [
                {"range": "A1:C3", "values": [["A1", "B1", "C1"]]},
                {"range": "D1:F3", "values": [["D1", "E1", "F1"]]},
            ]
        }

        result = read_ranges("test-id", ["A1:C3", "D1:F3"])

        assert len(result) == 2

    @patch("gwc.sheets.operations.get_sheets_service")
    def test_write_range(self, mock_service):
        """Test writing to a range."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.spreadsheets().values().update().execute.return_value = {
            "updatedRange": "Sheet1!A1:C3",
            "updatedRows": 3,
            "updatedColumns": 3,
            "updatedCells": 9,
        }

        values = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]
        result = write_range("test-id", "A1:C3", values)

        assert result["updatedRows"] == 3
        assert result["updatedCells"] == 9

    @patch("gwc.sheets.operations.get_sheets_service")
    def test_append_range(self, mock_service):
        """Test appending to a range."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.spreadsheets().values().append().execute.return_value = {
            "updates": {
                "updatedRange": "Sheet1!A10:C10",
                "updatedRows": 1,
                "updatedCells": 3,
            }
        }

        values = [["new", "row", "data"]]
        result = append_range("test-id", "A:C", values)

        assert result["updates"]["updatedRows"] == 1

    @patch("gwc.sheets.operations.get_sheets_service")
    def test_clear_range(self, mock_service):
        """Test clearing a range."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.spreadsheets().values().clear().execute.return_value = {
            "clearedRange": "Sheet1!A1:C10"
        }

        result = clear_range("test-id", "A1:C10")

        assert "A1:C10" in result["clearedRange"]

    @patch("gwc.sheets.operations.get_spreadsheet")
    def test_get_spreadsheet_stats(self, mock_get):
        """Test getting spreadsheet statistics."""
        mock_get.return_value = {
            "properties": {"title": "Stats Test"},
            "sheets": [
                {
                    "properties": {
                        "title": "Sheet1",
                        "gridProperties": {"rowCount": 1000, "columnCount": 26},
                    }
                },
                {
                    "properties": {
                        "title": "Sheet2",
                        "gridProperties": {"rowCount": 500, "columnCount": 10},
                    }
                },
            ],
        }

        result = get_spreadsheet_stats("test-id")

        assert result["title"] == "Stats Test"
        assert result["sheet_count"] == 2
        assert result["total_cells"] == (1000 * 26) + (500 * 10)

    def test_format_range_data_unix(self):
        """Test formatting data as unix (tab-separated)."""
        data = {
            "values": [["a", "b", "c"], ["1", "2", "3"], ["x", "y", "z"]]
        }

        result = format_range_data(data, "unix")

        lines = result.split("\n")
        assert len(lines) == 3
        assert lines[0] == "a\tb\tc"
        assert lines[1] == "1\t2\t3"

    def test_format_range_data_csv(self):
        """Test formatting data as CSV."""
        data = {
            "values": [["name", "age"], ["alice", "30"], ["bob", "25"]]
        }

        result = format_range_data(data, "csv")

        lines = result.split("\n")
        assert "name,age" in lines[0]

    def test_format_range_data_json(self):
        """Test formatting data as JSON."""
        data = {
            "range": "A1:B2",
            "values": [["a", "b"], ["1", "2"]],
        }

        result = format_range_data(data, "json")

        parsed = json.loads(result)
        assert parsed["range"] == "A1:B2"
        assert len(parsed["values"]) == 2


class TestPhase3SheetStructure:
    """Test Phase 3: Sheet structure operations."""

    @patch("gwc.sheets.operations.get_sheets_service")
    def test_add_sheet(self, mock_service):
        """Test adding a new sheet."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.spreadsheets().batchUpdate().execute.return_value = {
            "replies": [
                {
                    "addSheet": {
                        "properties": {
                            "sheetId": 123,
                            "title": "NewSheet",
                            "gridProperties": {
                                "rowCount": 1000,
                                "columnCount": 26,
                            },
                        }
                    }
                }
            ]
        }

        result = add_sheet("test-id", "NewSheet", rows=1000, columns=26)

        assert result["replies"][0]["addSheet"]["properties"]["title"] == "NewSheet"

    @patch("gwc.sheets.operations.get_sheets_service")
    def test_delete_sheet(self, mock_service):
        """Test deleting a sheet."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.spreadsheets().batchUpdate().execute.return_value = {
            "spreadsheetId": "test-id"
        }

        result = delete_sheet("test-id", 123)

        assert result["spreadsheetId"] == "test-id"

    @patch("gwc.sheets.operations.get_sheets_service")
    def test_copy_sheet(self, mock_service):
        """Test copying a sheet."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.spreadsheets().batchUpdate().execute.return_value = {
            "spreadsheetId": "test-id"
        }

        result = copy_sheet("test-id", 123)

        assert result["spreadsheetId"] == "test-id"


class TestPhase4AdvancedOperations:
    """Test Phase 4: Advanced operations."""

    @patch("gwc.sheets.operations.get_sheets_service")
    def test_batch_update(self, mock_service):
        """Test batch update."""
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.spreadsheets().batchUpdate().execute.return_value = {
            "spreadsheetId": "test-id",
            "replies": [],
        }

        requests = [
            {"addSheet": {"properties": {"title": "NewSheet"}}},
        ]
        result = batch_update("test-id", requests)

        assert result["spreadsheetId"] == "test-id"

    @patch("gwc.sheets.operations.batch_update")
    def test_batch_update_from_file(self, mock_batch):
        """Test batch update from JSON file."""
        mock_batch.return_value = {"spreadsheetId": "test-id"}

        # Create test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "requests": [
                        {"addSheet": {"properties": {"title": "Sheet"}}},
                    ]
                },
                f,
            )
            temp_file = f.name

        try:
            result = batch_update_from_file("test-id", temp_file)
            assert result["spreadsheetId"] == "test-id"
        finally:
            import os
            os.unlink(temp_file)
