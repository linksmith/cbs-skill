#!/usr/bin/env python3
"""
Comprehensive test suite for CBS StatLine client.
Tests all functionality and reports issues.
"""

import sys
import warnings
from datetime import date

import pandas as pd

from cbs_client import (
    CBSClient,
    TableMetadata,
    CBS_ODATA_V4_BASE,
    DEFAULT_TIMEOUT,
    TABLE_ID_PATTERN,
    __version__,
)


def test_version():
    """Test that version is defined."""
    print(f"✓ Version: {__version__}")
    assert __version__ == "1.1.0"


def test_constants():
    """Test module constants."""
    print("✓ Testing constants...")
    assert DEFAULT_TIMEOUT == 30
    assert TABLE_ID_PATTERN.pattern == r"^[0-9]{5}[A-Z]{3}$"
    assert "cbs.nl" in CBS_ODATA_V4_BASE


def test_client_init():
    """Test CBSClient initialization."""
    print("✓ Testing CBSClient initialization...")
    client = CBSClient()
    assert client.base_url == CBS_ODATA_V4_BASE
    assert client.delay == 0.3
    assert client.session is not None
    assert "Accept" in client.session.headers
    client.session.close()


def test_context_manager():
    """Test context manager pattern."""
    print("✓ Testing context manager...")
    with CBSClient() as client:
        assert client.session is not None
    # Session should be closed after exit
    # We can't directly test if it's closed, but we can check it doesn't raise


def test_table_id_validation():
    """Test table ID validation."""
    print("✓ Testing table_id validation...")
    client = CBSClient()

    # Valid IDs (including case variations)
    valid_ids = ["84518NED", "82900NED", "12345ABC", "00000XYZ", "84518ned", "12345abc"]
    for table_id in valid_ids:
        try:
            normalized = client._validate_table_id(table_id)
            # Should return uppercase normalized ID
            assert normalized == table_id.upper()
        except ValueError as e:
            print(f"  ✗ Valid ID rejected: {table_id} - {e}")
            raise

    # Invalid IDs
    invalid_ids = [
        "84518NEDX",  # too long
        "8451NED",  # too short
        "84518NE1",  # numbers in suffix
        "84518NE",  # incomplete suffix
        "abcdeFGH",  # letters in prefix
        "",  # empty
        "invalid",  # completely wrong
    ]

    for table_id in invalid_ids:
        try:
            client._validate_table_id(table_id)
            print(f"  ✗ Invalid ID accepted: {table_id}")
            raise AssertionError(f"Invalid ID should have been rejected: {table_id}")
        except ValueError:
            pass  # Expected

    client.session.close()


def test_period_parsing():
    """Test period code parsing."""
    print("✓ Testing period parsing...")

    # Valid period codes
    test_cases = [
        ("2023JJ00", (date(2023, 1, 1), "year")),
        ("2023KW01", (date(2023, 1, 1), "quarter")),
        ("2023KW04", (date(2023, 10, 1), "quarter")),
        ("2023MM06", (date(2023, 6, 1), "month")),
        ("2023MM12", (date(2023, 12, 1), "month")),
        ("2020JJ00", (date(2020, 1, 1), "year")),
    ]

    for code, expected in test_cases:
        result = CBSClient.parse_period(code)
        assert result == expected, (
            f"Failed for {code}: got {result}, expected {expected}"
        )

    # Invalid period codes
    invalid_codes = [
        "2023KW05",  # Invalid quarter (5)
        "2023KW00",  # Invalid quarter (0)
        "2023MM13",  # Invalid month (13)
        "2023MM00",  # Invalid month (0)
        "invalid",  # Invalid format
        "",  # Empty
        None,  # None
        "2023X000",  # Unknown frequency (should still work)
    ]

    for code in invalid_codes[:6]:
        result = CBSClient.parse_period(code)
        assert result == (None, None), (
            f"Invalid code should return (None, None): {code}"
        )

    # Test unknown frequency (should return date with "half-year" label)
    result = CBSClient.parse_period("2023X000")
    assert result[0] == date(2023, 1, 1)
    assert result[1] == "half-year"


def test_period_validation_warnings():
    """Test that period validation warns on invalid quarters/months."""
    print("✓ Testing period validation warnings...")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = CBSClient.parse_period("2023KW05")
        assert result == (None, None)
        assert len(w) == 1
        assert "Invalid quarter" in str(w[0].message)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = CBSClient.parse_period("2023MM13")
        assert result == (None, None)
        assert len(w) == 1
        assert "Invalid month" in str(w[0].message)


def test_region_cleaning():
    """Test region code cleaning."""
    print("✓ Testing region cleaning...")

    df = pd.DataFrame(
        {
            "RegioS": [
                "GM0344 ",
                "WK034400  ",
                "BU03440001",
                "NL00",
                "PV28",
                "  GM0363  ",
            ]
        }
    )

    cleaned = CBSClient.clean_regions(df)

    assert cleaned["RegioS"].tolist() == [
        "GM0344",
        "WK034400",
        "BU03440001",
        "NL00",
        "PV28",
        "GM0363",
    ]
    assert "region_level" in cleaned.columns
    assert cleaned["region_level"].tolist() == [
        "gemeente",
        "wijk",
        "buurt",
        "nederland",
        "provincie",
        "gemeente",
    ]


def test_region_filtering():
    """Test region level filtering."""
    print("✓ Testing region filtering...")

    df = pd.DataFrame(
        {"RegioS": ["GM0344", "WK034400", "BU03440001", "NL00", "PV28", "GM0363"]}
    )

    gemeentes = CBSClient.filter_region_level(df, "gemeente")
    assert len(gemeentes) == 2
    assert all(gemeentes["RegioS"].str.startswith("GM"))

    provincies = CBSClient.filter_region_level(df, "provincie")
    assert len(provincies) == 1
    assert provincies["RegioS"].iloc[0] == "PV28"


def test_add_date_column():
    """Test date column addition."""
    print("✓ Testing add_date_column...")

    df = pd.DataFrame({"Perioden": ["2023JJ00", "2023KW01", "2023MM06"]})

    result = CBSClient.add_date_column(df)

    assert "date" in result.columns
    assert "frequency" in result.columns
    assert result["date"].iloc[0] == date(2023, 1, 1)
    assert result["frequency"].iloc[0] == "year"
    assert result["frequency"].iloc[1] == "quarter"
    assert result["frequency"].iloc[2] == "month"


def test_metadata_caching():
    """Test that metadata is cached."""
    print("✓ Testing metadata caching...")

    client = CBSClient()

    # First call should create cache
    assert not hasattr(client, "_metadata_cache")

    # Manually test cache structure
    client._metadata_cache = {}
    client._metadata_cache["84518NED"] = TableMetadata(table_id="84518NED")

    # Should return cached version
    result = client.get_metadata("84518NED", use_cache=True)
    assert result.table_id == "84518NED"

    # Should skip cache when use_cache=False
    # (This would make a real API call, so we skip it in unit tests)

    client.session.close()


def test_timeout_parameter():
    """Test that timeout is properly used."""
    print("✓ Testing timeout parameter...")

    client = CBSClient()

    # Check that _get_json accepts timeout parameter
    import inspect

    sig = inspect.signature(client._get_json)
    assert "timeout" in sig.parameters
    assert sig.parameters["timeout"].default == DEFAULT_TIMEOUT

    client.session.close()


def test_search_tables_filter_logic():
    """Test search table filter logic with mock data."""
    print("✓ Testing search_tables filter logic...")

    client = CBSClient()

    # Mock catalog cache
    client._catalog_cache = pd.DataFrame(
        {
            "Identifier": ["84518NED", "82900NED", "12345ABC"],
            "Title": ["Zonnestroom woningen", "Voorraad woningen", "Other table"],
            "Summary": ["Solar panels on houses", "Housing stock data", "Unrelated"],
            "Modified": ["2023-01-01", "2023-02-01", "2023-03-01"],
        }
    )

    # Test single term search
    results = client.search_tables("zonnestroom")
    assert len(results) == 1
    assert results.iloc[0]["Identifier"] == "84518NED"

    # Test multi-term search (AND logic)
    results = client.search_tables("woningen voorraad")
    assert len(results) == 1
    assert results.iloc[0]["Identifier"] == "82900NED"

    # Test case insensitivity
    results = client.search_tables("ZONNESTROOM")
    assert len(results) == 1

    client.session.close()


def test_table_metadata_class():
    """Test TableMetadata dataclass."""
    print("✓ Testing TableMetadata class...")

    meta = TableMetadata(
        table_id="84518NED",
        title="Test Table",
        measures=pd.DataFrame(
            {"Identifier": ["M1", "M2"], "Title": ["Measure 1", "Measure 2"]}
        ),
        dimensions={
            "Perioden": pd.DataFrame({"Identifier": ["2023JJ00"], "Title": ["2023"]})
        },
    )

    # Test measure_lookup
    lookup = meta.measure_lookup()
    assert lookup == {"M1": "Measure 1", "M2": "Measure 2"}

    # Test dimension_lookup
    lookup = meta.dimension_lookup("Perioden")
    assert lookup == {"2023JJ00": "2023"}

    # Test with empty data
    empty_meta = TableMetadata(table_id="EMPTY")
    assert empty_meta.measure_lookup() == {}
    assert empty_meta.dimension_lookup("Missing") == {}


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "=" * 70)
    print("CBS Client Test Suite")
    print("=" * 70 + "\n")

    tests = [
        test_version,
        test_constants,
        test_client_init,
        test_context_manager,
        test_table_id_validation,
        test_period_parsing,
        test_period_validation_warnings,
        test_region_cleaning,
        test_region_filtering,
        test_add_date_column,
        test_metadata_caching,
        test_timeout_parameter,
        test_search_tables_filter_logic,
        test_table_metadata_class,
    ]

    failed = []
    passed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            failed.append((test.__name__, e))

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {len(failed)} failed")
    print("=" * 70)

    if failed:
        print("\nFailed tests:")
        for name, error in failed:
            print(f"  - {name}: {error}")
        return False
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
