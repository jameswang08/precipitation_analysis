# Ignoring all imports as they are installed via venv
import xarray as xr # type: ignore
import rioxarray as rxr #type: ignore
import pandas as pd #type: ignore
import calendar
import os
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
ds = xr.open_dataset('Data/Models/CanCM4i/2018.nc', decode_times=False)
ds = ds['prec'].mean(dim='M')
ds = convert_precip(ds, time_dim='S')
grouped_ds = convert_time(ds, time_dim='S')

# Load baseline data
baseline_files = sorted(glob('Data/BaselineCleaned/*.nc'))
grouped_baseline = {}

for file in baseline_files:
    yyyymm = os.path.basename(file)[:6]
    time = pd.to_datetime(yyyymm, format='%Y%m')

    ds = xr.open_dataset(file)
    grouped_baseline[yyyymm] = ds





