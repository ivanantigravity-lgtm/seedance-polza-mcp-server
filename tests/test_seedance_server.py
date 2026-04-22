from seedance_polza_mcp_server.server import _compact_status, _validate_media_files


def test_compact_status_keeps_main_fields() -> None:
    data = {
        "id": "abc",
        "status": "pending",
        "model": "bytedance/seedance-2",
        "usage": {"cost_rub": 1.0},
    }
    result = _compact_status(data)
    assert result["id"] == "abc"
    assert result["status"] == "pending"


def test_validate_media_files_accepts_url() -> None:
    items = [{"type": "url", "data": "https://example.com/test.png"}]
    result = _validate_media_files(items)
    assert result == items
