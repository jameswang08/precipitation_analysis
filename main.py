# Ignoring all imports as they are installed via venv
import xarray as xr # type: ignore
import rioxarray as rxr #type: ignore
import pandas as pd #type: ignore
import calendar
import os
import numpy as np
from glob import glob

# Libraries for plotting
import matplotlib.pyplot as plt # type: ignore
import cartopy.crs as ccrs # type: ignore
import cartopy.feature as cfeature # type: ignore

def convert_precip(ds: xr.DataArray, time_dim='S') -> xr.DataArray:
    """
    Convert precipitation rate (mm/day) to total monthly precipitation (mm)
    Assumes time_dim values represent months since 1960-01.
    """
    months_since_1960 = ds[time_dim].values
    ref_date = pd.Timestamp("1960-01-01")
    dates = pd.to_datetime([ref_date + pd.DateOffset(months=int(m)) for m in months_since_1960])

    days_in_month = [calendar.monthrange(d.year, d.month)[1] for d in dates]
    days_da = xr.DataArray(days_in_month, dims=[time_dim], coords={time_dim: ds[time_dim]})
    monthly_total = ds * days_da

    return monthly_total

def convert_time(ds: xr.Dataset | xr.DataArray, time_dim='time') -> dict[str, xr.Dataset | xr.DataArray]:
    """
    Convert time from months since Jan 1960 to YYYYMM format then group by month.

    Returns:
    - A dictionary mapping YYYYMM strings to corresponding dataset slices.
    """
    # Convert time coordinate to YYYYMM strings
    months_since_1960 = ds[time_dim].values
    ref_date = pd.Timestamp("1960-01-01")
    dates = pd.to_datetime([ref_date + pd.DateOffset(months=int(m)) for m in months_since_1960])
    yyyymm = dates.strftime('%Y%m')

    # Create a DataArray with YYYYMM labels as coordinate
    ds_with_yyyymm = ds.assign_coords({time_dim: yyyymm})

    # Unique YYYYMM values
    unique_yyyymm = list(pd.unique(yyyymm))

    # Group and store subsets by YYYYMM key
    grouped = {}
    for key in unique_yyyymm:
        grouped[key] = ds_with_yyyymm.sel({time_dim: key})

    return grouped

# Helper function to extract time from filename
def extract_time_from_filename(file_path):
    basename = os.path.basename(file_path)
    time_str = basename[:6]  # Extract 'YYYYMM'
    return pd.to_datetime(time_str, format='%Y%m')

# Load prediction data and average ensemble models
# Store model data keyed by time
# Dimensions (L, Y, X)
# Vars prec
ds = xr.open_dataset('Data/Models/CanCM4i/2018.nc', decode_times=False)
ds = ds['prec'].mean(dim='M')
ds = convert_precip(ds, time_dim='S')
grouped_ds = convert_time(ds, time_dim='S')

# Load baseline data
baseline_files = sorted(glob('Data/BaselineCleaned/*.nc'))
grouped_baseline = {}

# Store baseline data keyed by time
# Dimensions (y, x)
# Vars precip and spatial_ref
for file in baseline_files:
    # Extract time from filename
    yyyymm = os.path.basename(file)[:6]
    # time = pd.to_datetime(yyyymm, format='%Y%m')

    ds = xr.open_dataset(file)
    grouped_baseline[yyyymm] = ds

# Compare model predictions with baseline data
# for l in np.arange(0.5, 12, 0.5):

model_slice = model_slice = grouped_ds['201801'].sel(L=.5)
model_slice = model_slice.rename({'Y': 'y', 'X': 'x'})

baseline_slice = grouped_baseline['201801']

# Shift model longitudes
model_slice = model_slice.assign_coords(
    x=((model_slice.x + 180) % 360) - 180
)
model_slice = model_slice.sortby('x')


model_interp = model_slice.interp(
    x=baseline_slice.x,
    y=baseline_slice.y
)

diff = model_interp - baseline_slice['precip']

print("Model stats:", model_slice.min().item(), model_slice.max().item())
print("Baseline stats:", baseline_slice['precip'].min().item(), baseline_slice['precip'].max().item())
print("Diff stats:")
print("  Mean:", diff.mean().item())
print("  Min:", diff.min().item())
print("  Max:", diff.max().item())
print("  NaNs:", np.isnan(diff).sum().item())


plt.figure(figsize=(10, 6))

# Set projection (e.g., PlateCarree for lat/lon)
ax = plt.axes(projection=ccrs.PlateCarree())

# Plot the difference data
diff.plot(ax=ax, cmap='RdBu_r', vmin=-5, vmax=5,  # adjust color limits as needed
          cbar_kwargs={'label': 'Precipitation Difference (mm)'})

# Add geographic features
ax.add_feature(cfeature.STATES, edgecolor='gray')  # US states borders
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS)

# Set extent to cover the US [lon_min, lon_max, lat_min, lat_max]
ax.set_extent([-125, -66.5, 24, 50], crs=ccrs.PlateCarree())

plt.title('Difference in Precipitation (Model - Baseline)')
plt.show()

print("Model x:", model_slice.x.min().item(), model_slice.x.max().item())
print("Baseline x:", baseline_slice.x.min().item(), baseline_slice.x.max().item())

print("Model y:", model_slice.y.min().item(), model_slice.y.max().item())
print("Baseline y:", baseline_slice.y.min().item(), baseline_slice.y.max().item())
print("Model CRS:", getattr(model_slice, 'rio', None))
print("Baseline CRS:", getattr(baseline_slice, 'rio', None))
