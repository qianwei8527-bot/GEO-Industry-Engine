from app.services.capability_service import get_capability_service


def test_public_capabilities_only_platform_standard():
    capabilities = get_capability_service().list_public()
    assert isinstance(capabilities, list)
    assert all(item.get("source_mode") == "platform_standard" for item in capabilities)
