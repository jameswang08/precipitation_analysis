import numpy as np
from joblib import load
import rioxarray
from utils.io import load_model_data
from rasterio.transform import from_origin


model_data = load_model_data("NCEP-CFSv2-Forecast")
model_data = model_data.where(model_data > 0)
model_data = model_data.squeeze(dim='date')

print(model_data)
print(np.isnan(model_data.values).sum())
print(model_data.dims)

month_map = {
    0.5: 'October',
    1.5: 'November',
    2.5: 'December',
    3.5: 'January',
    4.5: 'February',
    5.5: 'March',
    6.5: 'April',
    7.5: 'May',
    8.5: 'June',
    9.5: 'July'
}


for lead in np.arange(0.5, 10.0, 1.0):
    month_data = model_data.sel(L=lead)

    # Percentile scaling (based on this month's data)
    vmin = float(np.nanpercentile(month_data, 5))
    vmax = float(np.nanpercentile(month_data, 95))
    scaled = month_data.clip(min=vmin, max=vmax)
    normalized = (scaled - vmin) / (vmax - vmin)

    # Flip latitude
    normalized = normalized.isel(y=slice(None, None, -1))

    # Coordinates
    lons = normalized['x'].values
    lats = normalized['y'].values

    ulx = lons.min()
    uly = lats.max()
    pixel_width = lons[1] - lons[0]
    pixel_height = lats[0] - lats[1]

    transform = from_origin(ulx, uly, pixel_width, pixel_height)

    normalized = normalized.rio.set_spatial_dims(x_dim='x', y_dim='y', inplace=False)
    normalized = normalized.rio.write_crs("EPSG:4326", inplace=True)
    normalized = normalized.rio.write_transform(transform, inplace=True)

    filename = f"NCEP-CFSv2_{month_map[lead]}.tif"
    normalized.rio.to_raster(filename)
    print(f"✅ Exported GeoTIFF: {filename}")

