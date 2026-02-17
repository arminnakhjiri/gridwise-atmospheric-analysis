# -*- coding: utf-8 -*-
"""
Grid-level annual statistics from global raster datasets
Rasters: NDVI, PM2.5, PBLH, WindSpeed
Grid: 20 km × 20 km
Output: Excel file with Year, GridID (FID2), NDVI, PM2.5, PBLH, WindSpeed
"""

import rasterio
from rasterstats import zonal_stats
import geopandas as gpd
import pandas as pd
from pathlib import Path


# ------------------------------
# 1️⃣ File paths
# ------------------------------

grid_fp = r"C:\Users\lenovo\Downloads\biz paper no 1\data\vector\global_grid250in250km.shp"

rasters = {
    "Precipitation": {
        "path": r"C:\Users\lenovo\Downloads\biz paper no 1\data\raster\ERA5_TotalPrecip_1998_2022_multiband.tif",
        "start_year": 1998
    },
    "NDVI": {
        "path": r"C:\Users\lenovo\Downloads\biz paper no 1\data\raster\MODIS_NDVI_2000_2022_multiband.tif",
        "start_year": 2000
    },
    "PM25": {
        "path": r"C:\Users\lenovo\Downloads\biz paper no 1\data\raster\mosaic2.tif",
        "start_year": 1998
    },
    "PBLH": {
        "path": r"C:\Users\lenovo\Downloads\biz paper no 1\data\raster\PBLH_1998_2022_multiband.tif",
        "start_year": 1998
    },
    "WindSpeed": {
        "path": r"C:\Users\lenovo\Downloads\biz paper no 1\data\raster\ERA5_WindSpeed_1998_2022_multiband.tif",
        "start_year": 1998
    }
}

output_excel = Path(r"C:\Users\lenovo\Desktop\Grid_Level_Annual_Means.xlsx")

# ------------------------------
# 2️⃣ Load grid shapefile
# ------------------------------

grid = gpd.read_file(grid_fp)

# Use FID2 as unique ID
grid = grid[["FID2", "geometry"]]

# ------------------------------
# 3️⃣ Extract zonal statistics
# ------------------------------

records = []

for param, info in rasters.items():
    print(f"\nProcessing {param} ...")
    with rasterio.open(info["path"]) as src:
        nodata_val = src.nodata if src.nodata is not None else -9999

        for band in range(1, src.count + 1):
            year = info["start_year"] + band - 1
            print(f"  Band {band}/{src.count} → Year {year}")

            stats = zonal_stats(
                grid,
                info["path"],
                band=band,
                stats=["mean"],
                nodata=nodata_val,
                all_touched=False
            )

            for FID2, s in zip(grid["FID2"], stats):
                records.append({
                    "Year": year,
                    "GridID": FID2,
                    param: s["mean"]
                })
    print(f"Finished {param}")

# ------------------------------
# 4️⃣ Merge results into a single table
# ------------------------------

df = pd.DataFrame(records)

# Pivot so each parameter is a column
df_wide = df.pivot_table(
    index=["GridID", "Year"],
    values=list(rasters.keys())
).reset_index()

# ------------------------------
# 5️⃣ Save to Excel
# ------------------------------

df_wide.to_excel(output_excel, index=False)
print(f"\n✅ Finished! Excel saved at: {output_excel.resolve()}")
