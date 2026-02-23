# Grid-Level Annual Environmental Statistics from Global Rasters

This repository provides a **Python workflow** for extracting **grid-level annual mean values** from **global multi-band raster datasets** using zonal statistics.

The script computes annual averages of environmental variables (e.g., PM₂.₅, NDVI, PBLH, wind speed, precipitation) for each grid cell and exports the results to an Excel file suitable for statistical analysis (e.g., SPSS, R, Python).

---

## 📌 Overview

- **Spatial unit**: Regular global grid (e.g., 250 km × 250 km)
- **Temporal unit**: Annual (one raster band = one year)
- **Method**: Zonal mean statistics
- **Output**: Tabular dataset (Excel)

This approach avoids country-level aggregation bias and is well-suited for studying physical relationships between air quality, meteorology, and land surface properties.

---

## 📂 Input Data Requirements

### 1. Grid Shapefile
A polygon grid covering the global extent.

**Requirements:**
- Polygon geometry
- A unique grid identifier (e.g., `FID2`)

Example attributes:
```
FID2 | geometry
```

---

### 2. Raster Datasets
Multi-band GeoTIFF files where:
- Each band represents **one year**
- All rasters are **spatially aligned**
- All rasters share the **same projection**

Example variables:
- PM₂.₅ concentration
- NDVI
- Planetary Boundary Layer Height (PBLH)
- Wind speed
- Total precipitation

---

## 🧰 Python Dependencies

Install the required packages:

```bash
pip install rasterio geopandas rasterstats pandas openpyxl
```

---

## 🧪 Methodology

For each raster variable:
1. Loop through all bands (years)
2. Compute **mean pixel value** within each grid cell
3. Store results in long format
4. Pivot to wide format (one row per grid–year)
5. Export to Excel

---

## 🧾 Output Format

The final Excel file contains:

| GridID | Year | PM25 | NDVI | PBLH | WindSpeed | Precipitation |
|------|------|------|------|------|-----------|---------------|

This structure is ready for:
- Correlation analysis
- Regression models
- Panel data analysis
- Visualization

---

## 🧑‍💻 Full Python Script

```python
import rasterio
from rasterstats import zonal_stats
import geopandas as gpd
import pandas as pd
from pathlib import Path

grid_fp = "path/to/global_grid.shp"

rasters = {
    "Precipitation": {
        "path": "path/to/precipitation_multiband.tif",
        "start_year": 1998
    },
    "NDVI": {
        "path": "path/to/ndvi_multiband.tif",
        "start_year": 2000
    },
    "PM25": {
        "path": "path/to/pm25_multiband.tif",
        "start_year": 1998
    },
    "PBLH": {
        "path": "path/to/pblh_multiband.tif",
        "start_year": 1998
    },
    "WindSpeed": {
        "path": "path/to/windspeed_multiband.tif",
        "start_year": 1998
    }
}

output_excel = Path("Grid_Level_Annual_Means.xlsx")

grid = gpd.read_file(grid_fp)
grid = grid[["FID2", "geometry"]]

records = []

for param, info in rasters.items():
    with rasterio.open(info["path"]) as src:
        nodata_val = src.nodata if src.nodata is not None else -9999

        for band in range(1, src.count + 1):
            year = info["start_year"] + band - 1

            stats = zonal_stats(
                grid,
                info["path"],
                band=band,
                stats=["mean"],
                nodata=nodata_val,
                all_touched=False
            )

            for gid, s in zip(grid["FID2"], stats):
                records.append({
                    "Year": year,
                    "GridID": gid,
                    param: s["mean"]
                })

df = pd.DataFrame(records)

df_wide = df.pivot_table(
    index=["GridID", "Year"],
    values=list(rasters.keys())
).reset_index()

df_wide.to_excel(output_excel, index=False)
```

---

## 📄 License

MIT License

---

## Author
**Armin Nakhjiri**  
Remote Sensing Scientist 
✉️ Nakhjiri.Armin@gmail.com  

---

*Empowering the next generation of geospatial analysts, one script at a time.*
