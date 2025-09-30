import numpy as np
from joblib import load
import rioxarray
from rasterio.transform import from_origin

# Load joblib dataset
data = load("./cache/mac/CanCM4i_lead0.5_metrics.joblib")
model_data = data['Jan']['model_avg']

# Ensure NaNs for invalid/negative values
model_data = model_data.where(model_data > 0)

# Percentile scaling
vmin = float(np.nanpercentile(model_data, 5))
vmax = float(np.nanpercentile(model_data, 95))
scaled = model_data.clip(min=vmin, max=vmax)
normalized = (scaled - vmin) / (vmax - vmin)

# Rename dims to 'y' and 'x' (you already have them correctly)
normalized = normalized.rename({'lat': 'y', 'lon': 'x'}) if 'lat' in normalized.dims else normalized

# Flip along latitude (y) axis so that first row is northernmost latitude
normalized = normalized.isel(y=slice(None, None, -1))

# Get coordinate arrays after flipping
lons = normalized['x'].values
lats = normalized['y'].values

# Define transform with upper-left corner at min longitude, max latitude (after flipping)
ulx = lons.min()
uly = lats.max()

pixel_width = lons[1] - lons[0]
pixel_height = lats[0] - lats[1]  # positive because lats are descending after flip

print(f"Transform origin: ({ulx}, {uly}), pixel size: ({pixel_width}, {pixel_height})")

transform = from_origin(ulx, uly, pixel_width, pixel_height)

# Set spatial dims explicitly
normalized = normalized.rio.set_spatial_dims(x_dim='x', y_dim='y', inplace=False)

# Write CRS and transform
normalized = normalized.rio.write_crs("EPSG:4326", inplace=True)
normalized = normalized.rio.write_transform(transform, inplace=True)

# Save GeoTIFF
normalized.rio.to_raster("precipitation.tif")

print("✅ Exported GeoTIFF: precipitation.tif")
