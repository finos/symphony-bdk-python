import pytest

from symphony.bdk.core.service.user.user_util import NumberUtil, extract_tenant_id


def test_extract_tenant_id():
    tenant_id = 189
    user_id = 12987981103203

    assert extract_tenant_id(user_id) == tenant_id


def test_illegal_segments_size():
    with pytest.raises(ValueError):
        NumberUtil(sizes=[32, 32, 32])
