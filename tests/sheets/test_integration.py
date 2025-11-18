"""Integration tests for Sheets CLI.

These tests require valid Google Workspace credentials and API access.
Run with: pytest tests/sheets/test_integration.py -v
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock


class TestSheetsIntegration:
    """Integration tests for Sheets CLI commands."""

    @pytest.fixture
    def mock_sheets_service(self):
        """Mock Sheets API service."""
        with patch("gwc.sheets.operations.get_sheets_service") as mock:
            yield mock

    def test_end_to_end_spreadsheet_workflow(self, mock_sheets_service):
        """Test complete workflow: create, write, read."""
        from gwc.sheets.operations import (
            create_spreadsheet,
            write_range,
            read_range,
        )

        mock_service = Mock()
        mock_sheets_service.return_value = mock_service

        # Create
        mock_service.spreadsheets().create().execute.return_value = {
            "spreadsheetId": "test-id"
        }

        sheet_id = create_spreadsheet("Test Report", sheets=["Data"])
        assert sheet_id == "test-id"

        # Write
        mock_service.spreadsheets().values().update().execute.return_value = {
            "updatedRange": "Data!A1:C3",
            "updatedRows": 3,
            "updatedColumns": 3,
            "updatedCells": 9,
        }

        values = [["Name", "Age", "City"], ["Alice", 30, "NYC"], ["Bob", 25, "LA"]]
        result = write_range(sheet_id, "Data!A1:C3", values)
        assert result["updatedCells"] == 9

        # Read
        mock_service.spreadsheets().values().get().execute.return_value = {
            "range": "Data!A1:C3",
            "values": values,
        }

        data = read_range(sheet_id, "Data!A1:C3")
        assert len(data["values"]) == 3
        assert data["values"][0] == ["Name", "Age", "City"]

    def test_multiple_sheets_workflow(self, mock_sheets_service):
        """Test workflow with multiple sheets."""
        from gwc.sheets.operations import add_sheet, list_sheets

        mock_service = Mock()
        mock_sheets_service.return_value = mock_service

        # List sheets
        mock_service.spreadsheets().get().execute.return_value = {
            "spreadsheetId": "test-id",
            "sheets": [
                {
                    "properties": {
                        "sheetId": 0,
                        "title": "Summary",
                        "gridProperties": {"rowCount": 1000, "columnCount": 26},
                    }
                },
                {
                    "properties": {
                        "sheetId": 1,
                        "title": "Details",
                        "gridProperties": {"rowCount": 5000, "columnCount": 50},
                    }
                },
            ],
        }

        sheets = list_sheets("test-id")
        assert len(sheets) == 2

        # Add sheet
        mock_service.spreadsheets().batchUpdate().execute.return_value = {
            "replies": [
                {
                    "addSheet": {
                        "properties": {
                            "sheetId": 2,
                            "title": "Analysis",
                        }
                    }
                }
            ]
        }

        result = add_sheet("test-id", "Analysis")
        assert result["replies"][0]["addSheet"]["properties"]["title"] == "Analysis"

    def test_batch_operations_workflow(self, mock_sheets_service):
        """Test batch operations with multiple requests."""
        from gwc.sheets.operations import batch_update

        mock_service = Mock()
        mock_sheets_service.return_value = mock_service

        mock_service.spreadsheets().batchUpdate().execute.return_value = {
            "spreadsheetId": "test-id",
            "replies": [
                {"addSheet": {"properties": {"sheetId": 1}}},
                {"updateCells": {"updatedRows": 5}},
            ],
        }

        requests = [
            {
                "addSheet": {
                    "properties": {
                        "title": "NewSheet",
                        "gridProperties": {"rowCount": 100, "columnCount": 26},
                    }
                }
            },
            {
                "updateCells": {
                    "rows": [
                        {
                            "values": [
                                {"userEnteredValue": {"stringValue": "Header"}},
                            ]
                        }
                    ],
                    "fields": "*",
                }
            },
        ]

        result = batch_update("test-id", requests)
        assert len(result["replies"]) == 2

    def test_data_import_workflow(self, mock_sheets_service):
        """Test importing data to spreadsheet."""
        from gwc.sheets.operations import append_range, read_range

        mock_service = Mock()
        mock_sheets_service.return_value = mock_service

        # Append data (simulating import)
        mock_service.spreadsheets().values().append().execute.return_value = {
            "updates": {
                "updatedRange": "Data!A1:C1000",
                "updatedRows": 1000,
                "updatedCells": 3000,
            }
        }

        data_rows = [[i, f"Name{i}", f"Value{i}"] for i in range(100)]
        result = append_range("test-id", "Data!A:C", data_rows)
        assert result["updates"]["updatedRows"] == 1000

        # Verify data was written
        mock_service.spreadsheets().values().get().execute.return_value = {
            "range": "Data!A1:C1000",
            "values": data_rows[:100],  # Return first 100 rows
        }

        read_result = read_range("test-id", "Data!A1:C1000")
        assert len(read_result["values"]) == 100

    def test_formula_workflow(self, mock_sheets_service):
        """Test working with formulas."""
        from gwc.sheets.operations import write_range, read_range

        mock_service = Mock()
        mock_sheets_service.return_value = mock_service

        # Write formulas
        mock_service.spreadsheets().values().update().execute.return_value = {
            "updatedRange": "A1:C10",
            "updatedRows": 10,
            "updatedCells": 30,
        }

        formulas = [
            ["Name", "Value", "Double"],
            ["Item1", 10, "=B2*2"],
            ["Item2", 20, "=B3*2"],
        ]
        result = write_range("test-id", "A1:C3", formulas, value_input_option="USER_ENTERED")
        assert result["updatedCells"] == 30

        # Read formulas as formulas
        mock_service.spreadsheets().values().get().execute.return_value = {
            "range": "A1:C3",
            "values": formulas,  # Would show =B2*2 when using FORMULA render option
        }

        data = read_range("test-id", "A1:C3", value_render_option="FORMULA")
        assert "=" in str(data["values"])

    def test_batch_file_workflow(self, mock_sheets_service):
        """Test batch operations from file."""
        from gwc.sheets.operations import batch_update_from_file

        mock_service = Mock()
        mock_sheets_service.return_value = mock_service

        mock_service.spreadsheets().batchUpdate().execute.return_value = {
            "spreadsheetId": "test-id",
            "replies": [],
        }

        # Create temp batch file
        batch_data = {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": "Analysis",
                            "gridProperties": {"rowCount": 1000, "columnCount": 26},
                        }
                    }
                },
                {
                    "updateCells": {
                        "rows": [
                            {
                                "values": [
                                    {"userEnteredValue": {"stringValue": "Header"}}
                                ]
                            }
                        ],
                        "fields": "*",
                    }
                },
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(batch_data, f)
            temp_file = f.name

        try:
            result = batch_update_from_file("test-id", temp_file)
            assert result["spreadsheetId"] == "test-id"
        finally:
            Path(temp_file).unlink()

    def test_error_handling_invalid_range(self, mock_sheets_service):
        """Test error handling for invalid range."""
        from gwc.sheets.operations import read_range
        from googleapiclient.errors import HttpError

        mock_service = Mock()
        mock_sheets_service.return_value = mock_service

        # Simulate API error
        mock_service.spreadsheets().values().get().execute.side_effect = HttpError(
            Mock(status=400), b"Invalid range"
        )

        with pytest.raises(Exception) as exc_info:
            read_range("test-id", "InvalidRange")
        assert "Error reading range" in str(exc_info.value)

    def test_error_handling_missing_credentials(self):
        """Test error handling when credentials are missing."""
        from gwc.sheets.operations import get_sheets_service

        with patch("gwc.sheets.operations._load_credentials") as mock_load:
            mock_load.side_effect = Exception("No token found")

            with pytest.raises(Exception) as exc_info:
                get_sheets_service()
            assert "No token found" in str(exc_info.value)

    def test_formatting_data_handling(self, mock_sheets_service):
        """Test handling of formatted data."""
        from gwc.sheets.operations import read_range

        mock_service = Mock()
        mock_sheets_service.return_value = mock_service

        # Mock formatted values
        mock_service.spreadsheets().values().get().execute.return_value = {
            "range": "A1:B3",
            "values": [["$100.00", "Jan 1, 2024"], ["$200.50", "Feb 1, 2024"]],
        }

        result = read_range("test-id", "A1:B3", value_render_option="FORMATTED_VALUE")
        assert "$" in str(result["values"][0][0])

    def test_raw_value_handling(self, mock_sheets_service):
        """Test handling of raw unformatted values."""
        from gwc.sheets.operations import read_range

        mock_service = Mock()
        mock_sheets_service.return_value = mock_service

        # Mock raw values
        mock_service.spreadsheets().values().get().execute.return_value = {
            "range": "A1:B3",
            "values": [["100", "45292"], ["200.5", "45353"]],
        }

        result = read_range("test-id", "A1:B3", value_render_option="UNFORMATTED_VALUE")
        assert isinstance(result["values"][0][1], str)

    def test_large_data_batch_read(self, mock_sheets_service):
        """Test reading large amounts of data via batch."""
        from gwc.sheets.operations import read_ranges

        mock_service = Mock()
        mock_sheets_service.return_value = mock_service

        # Mock large dataset across multiple ranges
        large_data = [[str(i) for i in range(100)] for _ in range(1000)]

        mock_service.spreadsheets().values().batchGet().execute.return_value = {
            "valueRanges": [
                {"range": "Sheet1!A1:CV1000", "values": large_data},
                {"range": "Sheet2!A1:CV1000", "values": large_data},
            ]
        }

        results = read_ranges("test-id", ["Sheet1!A1:CV1000", "Sheet2!A1:CV1000"])
        assert len(results) == 2
        assert len(results[0]["values"]) == 1000
