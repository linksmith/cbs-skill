# Geographic Visualization with PDOK

## Overview

PDOK (Publieke Dienstverlening Op de Kaart) is the Dutch national geodata
portal. It provides boundary files (gemeenten, wijken, buurten, provincies)
that match CBS region codes — making it possible to create thematic maps
(choropleth/chloropleth) from CBS StatLine data.

## Getting boundary files

PDOK offers boundaries via a WFS (Web Feature Service) API and as downloadable
GeoJSON/Shapefile. For Python, the simplest approach is to use the
`cbsodata` package's built-in map support or download GeoJSON directly.

### Option A: Direct GeoJSON from PDOK (recommended)

```python
import geopandas as gpd

# Gemeente boundaries (most common for CBS data)
GEMEENTE_URL = (
    "https://service.pdok.nl/cbs/gebiedsindelingen/2023/wfs/v1_0"
    "?service=WFS&version=2.0.0&request=GetFeature"
    "&typeName=gebiedsindelingen:gemeente_gegeneraliseerd"
    "&outputFormat=json"
)
gemeenten = gpd.read_file(GEMEENTE_URL)

# Wijk boundaries
WIJK_URL = (
    "https://service.pdok.nl/cbs/gebiedsindelingen/2023/wfs/v1_0"
    "?service=WFS&version=2.0.0&request=GetFeature"
    "&typeName=gebiedsindelingen:wijk_gegeneraliseerd"
    "&outputFormat=json"
)
wijken = gpd.read_file(WIJK_URL)

# Buurt boundaries (large download!)
BUURT_URL = (
    "https://service.pdok.nl/cbs/gebiedsindelingen/2023/wfs/v1_0"
    "?service=WFS&version=2.0.0&request=GetFeature"
    "&typeName=gebiedsindelingen:buurt_gegeneraliseerd"
    "&outputFormat=json"
)
buurten = gpd.read_file(BUURT_URL)

# Provincie boundaries
PROVINCIE_URL = (
    "https://service.pdok.nl/cbs/gebiedsindelingen/2023/wfs/v1_0"
    "?service=WFS&version=2.0.0&request=GetFeature"
    "&typeName=gebiedsindelingen:provincie_gegeneraliseerd"
    "&outputFormat=json"
)
provincies = gpd.read_file(PROVINCIE_URL)
```

### Important: Year matching

PDOK publishes boundaries per year (gemeenten merge, split, rename). Use
the same year as your CBS data:
- Replace `2023` in the URL with the relevant year
- Available years: typically 2015–present

### Option B: Using cartomap from CBS GitHub

CBS publishes simplified map boundaries on their GitHub:
```python
# Alternative: CBS publishes GeoJSON via their own services
# These are simpler and may be easier for quick prototyping
import requests
import json

url = "https://cartomap.github.io/nl/wgs84/gemeente_2023.geojson"
gemeenten = gpd.read_file(url)
```

## Joining CBS data with geodata

The critical step: matching CBS region codes to PDOK boundary codes.

```python
import pandas as pd
import geopandas as gpd

# 1. Load your CBS data (already processed)
cbs_data = pd.read_csv("my_cbs_data.csv")

# 2. Normalise region codes
# CBS uses "GM0344  " (with spaces), PDOK uses "GM0344"
cbs_data["RegioS"] = cbs_data["RegioS"].str.strip()

# 3. Load gemeente boundaries
gemeenten = gpd.read_file(GEMEENTE_URL)

# 4. PDOK uses "statcode" as the key column
# Check what the key column is called:
print(gemeenten.columns.tolist())
# Usually: 'statcode', 'statnaam', 'geometry'

# 5. Join
merged = gemeenten.merge(
    cbs_data,
    left_on="statcode",
    right_on="RegioS",
    how="left"
)

# 6. Check for unmatched regions
unmatched = merged[merged["Value"].isna()]
if len(unmatched) > 0:
    print(f"Warning: {len(unmatched)} regions have no data")
```

## Creating thematic maps

### Static map (Matplotlib)

```python
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

fig, ax = plt.subplots(1, 1, figsize=(10, 12))

merged.plot(
    column="solar_percentage",  # Your measure column
    ax=ax,
    legend=True,
    legend_kwds={
        "label": "% woningen met zonnepanelen",
        "orientation": "horizontal",
        "shrink": 0.6
    },
    cmap="YlOrRd",  # Yellow-to-Red colour scale
    missing_kwds={"color": "lightgrey", "label": "Geen data"},
    edgecolor="white",
    linewidth=0.2
)

ax.set_title("Zonnepanelen per gemeente, 2023", fontsize=14, fontweight="bold")
ax.set_axis_off()

# Add source attribution (required for CBS data)
fig.text(0.5, 0.02, "Bron: CBS StatLine, tabel 85005NED (CC BY 4.0)",
         ha="center", fontsize=8, style="italic")

plt.tight_layout()
plt.savefig("solar_map.png", dpi=150, bbox_inches="tight")
plt.show()
```

### Interactive map (Plotly)

```python
import plotly.express as px
import json

# Convert GeoDataFrame to GeoJSON for Plotly
geojson = json.loads(merged.to_json())

fig = px.choropleth_mapbox(
    merged,
    geojson=geojson,
    locations=merged.index,
    color="solar_percentage",
    hover_name="statnaam",
    hover_data={"solar_percentage": ":.1f"},
    color_continuous_scale="YlOrRd",
    mapbox_style="carto-positron",
    center={"lat": 52.2, "lon": 5.3},
    zoom=6,
    opacity=0.7,
    labels={"solar_percentage": "% zonnepanelen"}
)

fig.update_layout(
    title="Zonnepanelen per gemeente",
    margin={"r": 0, "t": 40, "l": 0, "b": 0}
)
fig.show()
```

### Interactive map (Folium — lightweight alternative)

```python
import folium

m = folium.Map(location=[52.2, 5.3], zoom_start=7, tiles="cartodbpositron")

folium.Choropleth(
    geo_data=json.loads(merged.to_json()),
    data=merged,
    columns=["statcode", "solar_percentage"],
    key_on="feature.properties.statcode",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="% woningen met zonnepanelen"
).add_to(m)

m.save("solar_map.html")
```

## Dependencies

```
pip install geopandas folium plotly mapclassify
```

Note: `geopandas` requires `fiona`, `shapely`, and `pyproj`. On some systems
these have C dependencies. If installation fails:

```bash
# On Ubuntu/Debian
sudo apt-get install libgdal-dev libgeos-dev libproj-dev

# Or use conda (easier for geo stack)
conda install geopandas folium plotly
```

## Colour scale suggestions for energy/housing themes

| Theme | Recommended cmap | Why |
|---|---|---|
| Solar adoption (%) | `YlOrRd` | Warm colours = more sun |
| Gas consumption (m³) | `RdYlGn_r` | Red = high gas (bad), Green = low |
| Gas-free homes (%) | `RdYlGn` | Green = more gas-free (good) |
| Energy label (A→G) | `RdYlGn` | Green = A label, Red = G |
| Housing prices (€) | `viridis` | Neutral, sequential |
| Year-over-year change (%) | `RdBu` | Diverging: red = decrease, blue = increase |

## Attribution

All CBS data is licensed CC BY 4.0. Always include:
- "Bron: CBS StatLine" in your visualisation
- The table ID and year
- "Kaartgegevens: PDOK/CBS Gebiedsindelingen" for the map boundaries
