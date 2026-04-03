"""
CBS StatLine OData v4 Client

A self-contained Python module for accessing CBS StatLine data via the OData v4 API.
Designed for data journalism hackathons focused on housing and energy transition.

Dependencies: requests, pandas
Install: pip install requests pandas

Usage:
    from cbs_client import CBSClient
    client = CBSClient()

    # Search for tables
    results = client.search_tables("zonnestroom woningen")

    # Inspect a table
    meta = client.get_metadata("84518NED")
    meta.show()

    # Download data
    df = client.get_data("84518NED", filters={"Perioden": "2023JJ00"})

    # Resolve codes to labels
    df = client.add_labels(df, "84518NED")

License: CC0 (public domain) — do whatever you want with this.
"""

import re
import time
import warnings
from datetime import date
from dataclasses import dataclass, field
from typing import Optional, Tuple

import pandas as pd
import requests

__version__ = "1.1.0"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CBS_ODATA_V4_BASE = "https://datasets.cbs.nl/odata/v1/CBS"
CBS_ODATA_V3_FEED = "https://opendata.cbs.nl/ODataFeed/OData"
CBS_ODATA_V3_API = "https://opendata.cbs.nl/ODataApi/OData"
CBS_CATALOG_V4 = "https://datasets.cbs.nl/odata/v1/CBS"

REQUEST_DELAY = 0.3
MAX_PAGES = 200
DEFAULT_TIMEOUT = 30
TABLE_ID_PATTERN = re.compile(r"^[0-9]{5}[A-Z]{3}$")


# ---------------------------------------------------------------------------
# Metadata container
# ---------------------------------------------------------------------------


@dataclass
class TableMetadata:
    """Container for CBS table metadata with human-readable display."""

    table_id: str
    title: str = ""
    description: str = ""
    status: str = ""
    modified: str = ""
    measures: pd.DataFrame = field(default_factory=pd.DataFrame)
    dimensions: dict = field(default_factory=dict)  # name → DataFrame of codes
    raw_properties: dict = field(default_factory=dict)

    def show(self):
        """Print a human-readable summary of the table metadata."""
        print(f"{'=' * 70}")
        print(f"Table: {self.table_id}")
        print(f"Title: {self.title}")
        print(f"Status: {self.status}")
        print(f"Modified: {self.modified}")
        print(f"{'=' * 70}")

        if not self.measures.empty:
            print(f"\nMeasures ({len(self.measures)}):")
            cols = [
                c for c in ["Identifier", "Title", "Unit"] if c in self.measures.columns
            ]
            print(self.measures[cols].to_string(index=False))

        for dim_name, dim_df in self.dimensions.items():
            print(f"\nDimension: {dim_name} ({len(dim_df)} categories)")
            cols = [c for c in ["Identifier", "Title"] if c in dim_df.columns]
            if len(dim_df) <= 20:
                print(dim_df[cols].to_string(index=False))
            else:
                print(dim_df[cols].head(10).to_string(index=False))
                print(f"  ... and {len(dim_df) - 10} more")

    def measure_lookup(self) -> dict:
        """Return {Identifier: Title} mapping for measures."""
        if self.measures.empty:
            return {}
        return dict(zip(self.measures["Identifier"], self.measures["Title"]))

    def dimension_lookup(self, dim_name: str) -> dict:
        """Return {Identifier: Title} mapping for a dimension."""
        if dim_name not in self.dimensions:
            return {}
        df = self.dimensions[dim_name]
        return dict(zip(df["Identifier"], df["Title"]))


# ---------------------------------------------------------------------------
# Main client
# ---------------------------------------------------------------------------


class CBSClient:
    """Client for CBS StatLine OData v4 API."""

    def __init__(self, base_url: str = CBS_ODATA_V4_BASE, delay: float = REQUEST_DELAY):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def __enter__(self) -> "CBSClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.session.close()

    def _validate_table_id(self, table_id: str) -> str:
        """Validate and normalize table ID to uppercase."""
        normalized = table_id.upper()
        if not TABLE_ID_PATTERN.match(normalized):
            raise ValueError(
                f"Invalid table_id '{table_id}'. Expected format: 5 digits + 3 letters (e.g., '84518NED')"
            )
        return normalized

    def _get_json(
        self, url: str, params: Optional[dict] = None, timeout: float = DEFAULT_TIMEOUT
    ) -> dict:
        time.sleep(self.delay)
        resp = self.session.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def _paginate(self, url: str, params: Optional[dict] = None) -> pd.DataFrame:
        """Fetch all pages from an OData endpoint, following @odata.nextLink."""
        all_rows = []
        current_url = url
        page = 0

        while current_url and page < MAX_PAGES:
            data = self._get_json(current_url, params=params)
            rows = data.get("value", [])
            all_rows.extend(rows)
            current_url = data.get("@odata.nextLink")
            params = None  # nextLink includes params already
            page += 1

            if page % 5 == 0 and current_url:
                print(f"  ... downloaded {len(all_rows)} rows ({page} pages)...")

        if page >= MAX_PAGES:
            warnings.warn(
                f"Reached pagination limit ({MAX_PAGES} pages, {len(all_rows)} rows). "
                "Consider adding filters to reduce the dataset."
            )

        return pd.DataFrame(all_rows)

    # -------------------------------------------------------------------
    # Catalog search
    # -------------------------------------------------------------------

    def search_tables(self, query: str, language: str = "nl") -> pd.DataFrame:
        """
        Search the CBS table catalog by keyword.

        Returns a DataFrame with table ID, title, summary, and modified date.
        Searches in title and summary fields (case-insensitive).

        Args:
            query: Search terms (space-separated, matches any)
            language: 'nl' (default) or 'en'
        """
        # Download full catalog (cached after first call)
        if not hasattr(self, "_catalog_cache"):
            print("Downloading CBS table catalog (one-time)...")
            url = f"{self.base_url}/Datasets?$format=json"
            self._catalog_cache = self._paginate(url)

        catalog = self._catalog_cache.copy()

        # Search across title and summary
        terms = query.lower().split()
        mask = pd.Series([True] * len(catalog))
        search_cols = ["Title", "Description", "ShortTitle"]
        available_cols = [c for c in search_cols if c in catalog.columns]

        for term in terms:
            term_mask = pd.Series([False] * len(catalog))
            for col in available_cols:
                term_mask |= (
                    catalog[col].fillna("").str.lower().str.contains(term, regex=False)
                )
            mask &= term_mask

        results = catalog[mask].copy()

        display_cols = [
            c for c in ["Identifier", "Title", "Modified"] if c in results.columns
        ]
        if display_cols:
            return results[display_cols].reset_index(drop=True)
        return results.reset_index(drop=True)

    # -------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------

    def get_metadata(self, table_id: str, use_cache: bool = True) -> TableMetadata:
        """
        Fetch complete metadata for a CBS table.

        Returns a TableMetadata object with measures, dimensions, and properties.
        Results are cached by table_id for the lifetime of the client instance.
        """
        normalized_id = self._validate_table_id(table_id)

        if (
            use_cache
            and hasattr(self, "_metadata_cache")
            and normalized_id in self._metadata_cache
        ):
            return self._metadata_cache[normalized_id]

        if not hasattr(self, "_metadata_cache"):
            self._metadata_cache = {}

        table_url = f"{self.base_url}/{normalized_id}"

        props = {}
        try:
            props_data = self._get_json(f"{table_url}/Properties")
            props = (
                props_data.get("value", [{}])[0]
                if "value" in props_data
                else props_data
            )
        except requests.RequestException as e:
            warnings.warn(f"Failed to fetch properties for {table_id}: {e}")

        measures_df = pd.DataFrame()
        try:
            measures_df = self._paginate(f"{table_url}/MeasureCodes")
        except requests.RequestException as e:
            warnings.warn(f"Failed to fetch measure codes for {table_id}: {e}")

        dimensions = {}
        try:
            root = self._get_json(table_url)
            for item in root.get("value", []):
                name = item.get("name", "")
                if name.endswith("Codes") and name != "MeasureCodes":
                    dim_name = name.replace("Codes", "")
                    try:
                        dim_df = self._paginate(f"{table_url}/{name}")
                        dimensions[dim_name] = dim_df
                    except requests.RequestException as e:
                        warnings.warn(f"Failed to fetch dimension {dim_name}: {e}")
        except requests.RequestException as e:
            warnings.warn(f"Failed to discover dimensions for {table_id}: {e}")

        result = TableMetadata(
            table_id=normalized_id,
            title=props.get("Title", ""),
            description=props.get("Description", ""),
            status=props.get("Status", ""),
            modified=props.get("Modified", ""),
            measures=measures_df,
            dimensions=dimensions,
            raw_properties=props,
        )
        self._metadata_cache[normalized_id] = result
        return result

    # -------------------------------------------------------------------
    # Data retrieval
    # -------------------------------------------------------------------

    def get_data(
        self,
        table_id: str,
        filters: Optional[dict] = None,
        raw_filter: Optional[str] = None,
        select_measures: Optional[list] = None,
    ) -> pd.DataFrame:
        """
        Download data from a CBS OData v4 table.

        Args:
            table_id: CBS table identifier (e.g., '82900NED')
            filters: Dict of {dimension: value} for simple equality filters.
                     Value can be a string (single) or list (multiple with 'or').
                     Example: {"Perioden": "2023JJ00", "RegioS": ["GM0344", "GM0363"]}
            raw_filter: Raw OData $filter string (overrides filters dict)
            select_measures: List of measure identifiers to keep

        Returns:
            pandas DataFrame with the data
        """
        normalized_id = self._validate_table_id(table_id)
        url = f"{self.base_url}/{normalized_id}/Observations"
        params = {}

        # Build filter string
        if raw_filter:
            filter_str = raw_filter
        elif filters:
            clauses = []
            for dim, val in filters.items():
                if isinstance(val, list):
                    or_parts = [f"{dim} eq '{v}'" for v in val]
                    clauses.append(f"({' or '.join(or_parts)})")
                else:
                    clauses.append(f"{dim} eq '{val}'")
            filter_str = " and ".join(clauses)
        else:
            filter_str = None

        # Add measure filter if specified
        if select_measures:
            measure_clause = " or ".join([f"Measure eq '{m}'" for m in select_measures])
            if filter_str:
                filter_str = f"{filter_str} and ({measure_clause})"
            else:
                filter_str = measure_clause

        if filter_str:
            params["$filter"] = filter_str

        print(f"Downloading {table_id}...")
        if filter_str:
            print(f"  Filter: {filter_str}")

        df = self._paginate(url, params=params)

        if not df.empty:
            print(f"  Got {len(df)} rows")

        return df

    def get_data_wide(
        self,
        table_id: str,
        filters: Optional[dict] = None,
        raw_filter: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Download data and pivot to wide format with human-readable column names.

        This converts the OData v4 long format (Measure/Value) into a familiar
        wide table where each measure becomes a column.
        """
        # Get data and metadata
        df = self.get_data(table_id, filters=filters, raw_filter=raw_filter)
        if df.empty:
            return df

        meta = self.get_metadata(table_id)
        measure_labels = meta.measure_lookup()

        # Identify dimension columns (everything except Id, Measure, Value, ValueAttribute)
        non_dim_cols = {"Id", "Measure", "Value", "ValueAttribute"}
        dim_cols = [c for c in df.columns if c not in non_dim_cols]

        # Replace measure codes with titles
        df["MeasureLabel"] = df["Measure"].map(measure_labels).fillna(df["Measure"])

        # Pivot
        wide = df.pivot_table(
            index=dim_cols, columns="MeasureLabel", values="Value", aggfunc="first"
        ).reset_index()

        # Resolve dimension codes to labels
        for dim_name, dim_df in meta.dimensions.items():
            if dim_name in wide.columns:
                lookup = dict(zip(dim_df["Identifier"], dim_df["Title"]))
                wide[f"{dim_name}_label"] = wide[dim_name].map(
                    lambda x: lookup.get(str(x).strip(), x)
                )

        return wide

    # -------------------------------------------------------------------
    # Label resolution
    # -------------------------------------------------------------------

    def add_labels(self, df: pd.DataFrame, table_id: str) -> pd.DataFrame:
        """
        Add human-readable label columns for all coded dimensions.

        For each dimension column in the DataFrame, adds a '{dim}_label' column.
        Also adds 'Measure_label' if a 'Measure' column exists.
        """
        meta = self.get_metadata(table_id)
        df = df.copy()

        # Measure labels
        if "Measure" in df.columns:
            lookup = meta.measure_lookup()
            df["Measure_label"] = df["Measure"].map(lookup).fillna(df["Measure"])

        # Dimension labels
        for dim_name, dim_df in meta.dimensions.items():
            if dim_name in df.columns:
                lookup = dict(zip(dim_df["Identifier"], dim_df["Title"]))
                df[f"{dim_name}_label"] = df[dim_name].apply(
                    lambda x: lookup.get(str(x).strip(), x)
                )

        return df

    # -------------------------------------------------------------------
    # Convenience: region and period helpers
    # -------------------------------------------------------------------

    @staticmethod
    def parse_period(period_code: str) -> Tuple[Optional[date], Optional[str]]:
        """
        Parse a CBS period code into (date, frequency).

        Examples:
            '2023JJ00' → (date(2023, 1, 1), 'year')
            '2023KW01' → (date(2023, 1, 1), 'quarter')
            '2023MM06' → (date(2023, 6, 1), 'month')
            '2023X000' → (date(2023, 1, 1), 'half-year')

        Returns:
            Tuple of (date, frequency_str) or (None, None) if invalid.
        """
        if not period_code:
            return None, None

        code = str(period_code).strip()
        match = re.match(r"(\d{4})([A-Z]{2}|[A-Z]0)(\d{2})", code)
        if not match:
            return None, None

        year = int(match.group(1))
        freq = match.group(2)
        num = int(match.group(3))

        if freq == "JJ":
            return date(year, 1, 1), "year"
        elif freq == "KW":
            if not 1 <= num <= 4:
                warnings.warn(
                    f"Invalid quarter number {num} in period code '{period_code}'"
                )
                return None, None
            month = (num - 1) * 3 + 1
            return date(year, month, 1), "quarter"
        elif freq == "MM":
            if not 1 <= num <= 12:
                warnings.warn(
                    f"Invalid month number {num} in period code '{period_code}'"
                )
                return None, None
            return date(year, num, 1), "month"
        elif freq == "X0":
            if num == 0:
                return date(year, 1, 1), "half-year"
            elif num in (1, 2):
                month = (num - 1) * 6 + 1
                return date(year, month, 1), "half-year"
            else:
                warnings.warn(
                    f"Invalid half-year number {num} in period code '{period_code}'"
                )
                return None, None
        else:
            return date(year, 1, 1), f"other ({freq})"

    @staticmethod
    def add_date_column(df: pd.DataFrame, period_col: str = "Perioden") -> pd.DataFrame:
        """Add 'date' and 'frequency' columns parsed from CBS period codes."""
        df = df.copy()
        parsed = df[period_col].apply(CBSClient.parse_period)
        df["date"] = parsed.apply(lambda x: x[0])
        df["frequency"] = parsed.apply(lambda x: x[1])
        return df

    @staticmethod
    def clean_regions(df: pd.DataFrame, region_col: str = "RegioS") -> pd.DataFrame:
        """Strip whitespace from region codes and add a 'region_level' column."""
        df = df.copy()
        df[region_col] = df[region_col].str.strip()

        def _level(code):
            code = str(code).strip()
            for prefix, level in [
                ("BU", "buurt"),
                ("WK", "wijk"),
                ("GM", "gemeente"),
                ("CR", "corop"),
                ("PV", "provincie"),
                ("LD", "landsdeel"),
                ("NL", "nederland"),
            ]:
                if code.startswith(prefix):
                    return level
            return "unknown"

        df["region_level"] = df[region_col].apply(_level)
        return df

    @staticmethod
    def filter_region_level(
        df: pd.DataFrame, level: str, region_col: str = "RegioS"
    ) -> pd.DataFrame:
        """Filter DataFrame to a specific geographic level."""
        prefixes = {
            "buurt": "BU",
            "wijk": "WK",
            "gemeente": "GM",
            "corop": "CR",
            "provincie": "PV",
            "landsdeel": "LD",
            "nederland": "NL",
        }
        prefix = prefixes.get(level, level)
        df = df.copy()
        df[region_col] = df[region_col].str.strip()
        return df[df[region_col].str.startswith(prefix)]

    # -------------------------------------------------------------------
    # V3 fallback (for tables not yet on v4)
    # -------------------------------------------------------------------

    def get_data_v3(self, table_id: str, filters: Optional[str] = None) -> pd.DataFrame:
        """
        Fallback: download from OData v3 Feed endpoint.

        Args:
            table_id: CBS table identifier
            filters: OData v3 filter string (e.g., "RegioS eq 'GM0344'")

        Returns:
            pandas DataFrame in wide format (named columns)
        """
        normalized_id = self._validate_table_id(table_id)
        url = f"{CBS_ODATA_V3_FEED}/{normalized_id}/TypedDataSet"
        params = {}
        if filters:
            params["$filter"] = filters

        print(f"Downloading {normalized_id} via OData v3 Feed...")
        return self._paginate(url, params=params)


# ---------------------------------------------------------------------------
# Standalone usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    client = CBSClient()

    # Example: search for solar energy tables
    print("Searching for 'zonnestroom woningen'...")
    results = client.search_tables("zonnestroom woningen")
    print(results.head(10))

    # Example: inspect a table
    print("\nFetching metadata for 84518NED (zonnestroom wijk/buurt)...")
    meta = client.get_metadata("84518NED")
    meta.show()
