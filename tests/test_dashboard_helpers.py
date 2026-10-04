from dashboard.utils.i18n import T


def test_i18n_keys_match():
    assert set(T["en"]) == set(T["hi"])
    assert T["en"]["demo_notice"].startswith("Demo")


def test_common_imports():
    from dashboard.utils import common
    assert callable(common.bootstrap)
    assert callable(common.footer)
    assert callable(common.sidebar_filters)
    assert common.TEMPLATE["layout"]["font"]["family"].startswith("'Public Sans'")
