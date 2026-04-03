# CBS OData v4 API Guide

## Base URLs

CBS is transitioning from OData v3 to v4. This skill targets **v4**.

| Purpose | URL pattern |
|---|---|
| Catalog (list all tables) | `https://datasets.cbs.nl/odata/v1/CBS` |
| Table root | `https://datasets.cbs.nl/odata/v1/CBS/{TABLE_ID}` |
| Observations (data) | `https://datasets.cbs.nl/odata/v1/CBS/{TABLE_ID}/Observations` |
| Measure codes (metadata) | `https://datasets.cbs.nl/odata/v1/CBS/{TABLE_ID}/MeasureCodes` |
| Dimension codes | `https://datasets.cbs.nl/odata/v1/CBS/{TABLE_ID}/{DimensionName}Codes` |
| Properties (table info) | `https://datasets.cbs.nl/odata/v1/CBS/{TABLE_ID}/Properties` |

**Fallback for older tables**: If a table isn't on v4 yet, fall back to v3:
- Feed (bulk): `https://opendata.cbs.nl/ODataFeed/OData/{TABLE_ID}`
- API (limited): `https://opendata.cbs.nl/ODataApi/OData/{TABLE_ID}`

## OData v4 data model

Unlike v3 (which returns wide tables with named columns), v4 uses a **long/narrow**
format with generic column names:

```
Observations table:
| Id | Measure | Value | ValueAttribute | <Dimension1> | <Dimension2> | ...
```

- `Measure`: A code like `T001036` or `3000` — resolve via `MeasureCodes`
- `Value`: The numeric value (can be null)
- `ValueAttribute`: Explains missing values (e.g., "Geheim", "Nihil", "Onbekend")
- Dimension columns vary per table (e.g., `RegioS`, `Perioden`, `WijkenEnBuurten`)

This means you always need two steps: (1) download Observations and (2) download
code lists to make sense of the codes.

## Common API patterns

### Fetch table metadata (always do this first)

```python
import requests
import pandas as pd

TABLE_ID = "82900NED"
BASE = f"https://datasets.cbs.nl/odata/v1/CBS/{TABLE_ID}"

# Table properties (title, description, status)
props = requests.get(f"{BASE}/Properties").json()
print(f"Title: {props['value'][0]['Title']}")

# What measures (columns) are available?
measures = pd.DataFrame(requests.get(f"{BASE}/MeasureCodes").json()["value"])
print(measures[["Identifier", "Title", "Unit"]])

# What dimensions does this table have?
# Check the root endpoint for available sub-endpoints
root = requests.get(BASE).json()
for item in root["value"]:
    print(item["name"], item["url"])
```

### Download data with pagination

OData v4 returns max 100,000 cells per request. Use `@odata.nextLink` to paginate:

```python
def get_cbs_data(table_id, endpoint="Observations", params=None):
    """Download all rows from a CBS OData v4 endpoint with automatic pagination."""
    base_url = f"https://datasets.cbs.nl/odata/v1/CBS/{table_id}/{endpoint}"
    all_data = []
    url = base_url

    while url:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        all_data.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
        params = None  # nextLink already includes params
        print(f"  Downloaded {len(all_data)} rows...")

    return pd.DataFrame(all_data)
```

### Filter data (reduce download size)

OData v4 supports `$filter` to request only matching rows. This is essential
for large tables like Kerncijfers (83765NED).

```python
# Filter by region (gemeente Utrecht)
params = {"$filter": "RegioS eq 'GM0344'"}

# Filter by period (year 2023)
params = {"$filter": "Perioden eq '2023JJ00'"}

# Combine filters
params = {"$filter": "RegioS eq 'GM0344' and Perioden eq '2023JJ00'"}

# Filter by multiple values (use 'or')
params = {"$filter": "Perioden eq '2022JJ00' or Perioden eq '2023JJ00'"}

# Filter regions by prefix (all gemeenten)
# NOTE: OData v4 supports startswith()
params = {"$filter": "startswith(RegioS, 'GM')"}
```

### Select specific measures (reduce columns)

```python
# Only download specific measures
params = {"$filter": "Measure eq 'T001036' or Measure eq '3000'"}
```

### Resolve codes to labels

```python
def resolve_codes(table_id, dimension_name):
    """Fetch the code list for a dimension and return as lookup dict."""
    url = f"https://datasets.cbs.nl/odata/v1/CBS/{table_id}/{dimension_name}Codes"
    codes = pd.DataFrame(requests.get(url).json()["value"])
    return dict(zip(codes["Identifier"], codes["Title"]))

# Example: resolve region codes
region_labels = resolve_codes("82900NED", "RegioS")
# → {"NL01": "Nederland", "PV20": "Groningen", "GM0344": "Utrecht", ...}

# Example: resolve measure codes
measure_labels = resolve_codes("82900NED", "Measure")
# Note: for MeasureCodes the endpoint is "MeasureCodes", not "MeasureCodes"
```

## Period code parsing

CBS period codes encode both the time point and the frequency:

```python
import re
from datetime import date

def parse_cbs_period(period_code):
    """Parse a CBS period code into a Python date and frequency label."""
    code = period_code.strip()
    match = re.match(r"(\d{4})(\w{2})(\d{2})", code)
    if not match:
        return None, None

    year, freq, num = int(match.group(1)), match.group(2), int(match.group(3))

    if freq == "JJ":
        return date(year, 1, 1), "year"
    elif freq == "KW":
        month = (num - 1) * 3 + 1
        return date(year, month, 1), "quarter"
    elif freq == "MM":
        return date(year, num, 1), "month"
    else:
        return date(year, 1, 1), f"unknown ({freq})"
```

## Region code normalisation

```python
def normalise_region_code(code):
    """Strip whitespace and standardise CBS region codes."""
    return code.strip()

def region_level(code):
    """Determine the geographic level from a CBS region code."""
    code = normalise_region_code(code)
    if code.startswith("BU"):
        return "buurt"
    elif code.startswith("WK"):
        return "wijk"
    elif code.startswith("GM"):
        return "gemeente"
    elif code.startswith("CR"):
        return "corop"
    elif code.startswith("PV"):
        return "provincie"
    elif code.startswith("LD"):
        return "landsdeel"
    elif code.startswith("NL"):
        return "nederland"
    else:
        return "unknown"

def filter_to_level(df, level, region_col="RegioS"):
    """Filter a DataFrame to a specific geographic level."""
    df = df.copy()
    df[region_col] = df[region_col].str.strip()
    prefixes = {
        "buurt": "BU", "wijk": "WK", "gemeente": "GM",
        "corop": "CR", "provincie": "PV", "landsdeel": "LD",
        "nederland": "NL"
    }
    prefix = prefixes.get(level, level)
    return df[df[region_col].str.startswith(prefix)]
```

## Rate limiting and courtesy

CBS does not enforce strict rate limits but asks users to be respectful.
For the hackathon:
- Add a small delay (0.5s) between consecutive API calls
- Cache downloaded data locally (save to CSV/parquet) — don't re-download
  the same table repeatedly
- Use `$filter` aggressively to minimise data transfer
- For very large tables (wijk/buurt nationwide), download once and filter locally

## Troubleshooting

| Problem | Solution |
|---|---|
| Table not found on v4 | Try v3 endpoint at `opendata.cbs.nl` |
| Empty `value` array | Check if table is archived; try Properties endpoint |
| Measure codes are numbers, not human-readable | You must fetch MeasureCodes separately |
| Region codes don't match between tables | Strip whitespace and check prefix (GM vs WK) |
| `ValueAttribute` is not None | The value is missing — check the attribute for the reason |
| Download hangs | Table is very large — add $filter to reduce scope |

## v3 fallback (using cbsodata package)

Some tables may not yet be on v4. The `cbsodata` Python package wraps v3:

```python
import cbsodata
import pandas as pd

# List all tables
toc = pd.DataFrame(cbsodata.get_table_list())

# Search for housing tables
housing = toc[toc["Title"].str.contains("woning", case=False, na=False)]

# Download a table (v3 — returns wide format with named columns)
data = pd.DataFrame(cbsodata.get_data("82900NED"))

# Download with filter (v3 filter syntax)
data = pd.DataFrame(cbsodata.get_data(
    "82900NED",
    filters="RegioS eq 'GM0344'"
))

# Get metadata
meta = cbsodata.get_meta("82900NED", "DataProperties")
```

Note: `cbsodata` uses v3 (wide format). Column names are the actual measure
titles. This is simpler but limited to 10,000 cells per request via the
standard API (use Feed for larger downloads).
