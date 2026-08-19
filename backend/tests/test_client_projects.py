from app.api.v1.client_projects import _mask_code


def test_client_token_mask_keeps_prefix_and_suffix():
    code = "abcdefghijklmnopqrstuvwxyz123456"
    masked = _mask_code(code)
    assert masked.startswith("abcdefghijklmn")
    assert masked.endswith("3456")
    assert code not in masked


def test_short_client_token_mask():
    assert _mask_code("abc123") == "abc123••••"
