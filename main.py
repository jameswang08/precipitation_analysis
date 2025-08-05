# Ignoring all imports as they are installed via venv
import xarray as xr # type: ignore
import rioxarray as rxr #type: ignore
import pandas as pd #type: ignore
import calendar
from collections import defaultdict
import os
import numpy as np
from glob import glob
import seaborn as sns

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

def normalize_CanCM4i(grouped_ds, time_key='201801', lead=0.5):
    """
    Selects and preprocesses a model slice from the dataset:
    - Selects a time slice and lead time
    - Renames coordinate variables to match the baseline
    - Normalizes longitude to [-180, 180]
    - Sorts by longitude

    Parameters:
        grouped_ds (xarray.Dataset): The input dataset grouped by time.
        time_key (str): The time slice key to select (e.g., '201801').
        lead (float): The lead to select from the 'L' coordinate.

    Returns:
        xarray.Dataset: The prepared model slice.
    """

    model_slice = grouped_ds[time_key].sel(L=lead)
    model_slice = model_slice.rename({'Y': 'y', 'X': 'x'})
    model_slice = model_slice.assign_coords(
        x=((model_slice.x + 180) % 360) - 180
    )
    model_slice = model_slice.sortby('x')
    return model_slice

def calculate_baseline(date, lead):
    """
    Calculates baseline to compare prediction against by adding lead time to prediction date.

    Parameters:
        date (str): The base date in "YYYYMM" format.
        lead (float): The number of months to add to the base date.

    Returns:
        str: The resulting date in "YYYYMM" format
    """
    year = date[:4]
    month = int(date[4:6])
    month += lead
    month = int(month)

    if month > 12:
        month -= 11 # Since we start counting from 1 (Jan)
        year = str(int(year) + 1)

    return f"{year}{month:02d}"


def calculate_precip_difference(model_slice, baseline_slice):
    """
    Interpolates model_slice to the baseline_slice grid and calculates error stats
    - bias ratio
    - normalized rmse
    - anomaly correlation coefficient (not implemented)

    Parameters:
        model_slice (xarray.DataArray or xarray.Dataset): The model data to interpolate.
        baseline_slice (xarray.DataArray or xarray.Dataset): The baseline data with target grid.

    Returns:
        xarray.DataArray: The difference between interpolated model and baseline precipitation.
    """
    model_interp = model_slice.interp(
        x=baseline_slice.x,
        y=baseline_slice.y
    )
    diff = model_interp - baseline_slice['precip']

    bias = diff.mean().item()
    rmse = np.sqrt((diff ** 2).mean()).item()

    return bias, rmse


# Load prediction data and average ensemble models
# Store model data keyed by time
# Dimensions (L, Y, X)
# Vars prec
ds = xr.open_dataset('Data/Models/CanCM4i/2018.nc', decode_times=False)
ds = ds['prec'].mean(dim='M')
ds = convert_precip(ds, time_dim='S')
grouped_ds = convert_time(ds, time_dim='S')

# Store baseline data keyed by time
# Dimensions (y, x)
# Vars precip and spatial_ref
baseline_files = sorted(glob('Data/BaselineCleaned/*.nc'))
grouped_baseline = {}
for file in baseline_files:
    yyyymm = os.path.basename(file)[:6]
    ds = xr.open_dataset(file)
    grouped_baseline[yyyymm] = ds

# Compare model predictions with baseline data
results = defaultdict(list)
for month in grouped_ds.keys():
    print(f"Processing month: {month}")
    for l in np.arange(0.5, 12, 1):
        print(f"Processing lead time: {l}")

        # Rename vars to match baseline and normalize longitude
        model_slice = normalize_CanCM4i(grouped_ds, time_key=month, lead=float(l))
        baseline_slice = grouped_baseline[calculate_baseline(month, float(l))]

        bias_ratio, rmse = calculate_precip_difference(model_slice, baseline_slice)

        results[month].append({
            'lead': float(l),
            'bias_ratio': bias_ratio,
            'rmse': rmse,
        })

# Printing contents of results
for month, entries in results.items():
    print(f"Month: {month}")
    for entry in entries:
        print(f"  Lead: {entry['lead']}, Bias Ratio: {entry['bias_ratio']:.4f}, RMSE: {entry['rmse']:.4f}")