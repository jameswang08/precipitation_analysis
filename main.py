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
from typing import Dict, Union

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

def convert_time(ds: xr.Dataset | xr.DataArray, time_dim='S') -> Union[xr.DataArray, xr.Dataset]:
    """
    Convert time from months since Jan 1960 to YYYYMM format then group by month.
    """
    # Convert time coordinate to YYYYMM strings
    months_since_1960 = ds[time_dim].values
    ref_date = pd.Timestamp("1960-01-01")
    dates = pd.to_datetime([ref_date + pd.DateOffset(months=int(m)) for m in months_since_1960])
    yyyymm = dates.strftime('%Y%m')

    # Assign the new 'date' coordinate along the time_dim ('S')
    ds = ds.assign_coords(date=(time_dim, yyyymm))
    ds = ds.swap_dims({time_dim: "date"})
    ds = ds.drop_vars(time_dim)
    return ds


def load_model_data(model: str) -> Union[xr.Dataset, xr.DataArray]:
    """
    Loads and processes model prediction data from a NetCDF file.

    This function:
    - Loads the specified model NetCDF file
    - Averages across the ensemble member dimension ('M')
    - Converts precipitation rates (mm/day) to monthly totals (mm)
    - Converts the time coordinate from numeric format (months since 1960-01)
      to string format (YYYYMM), and groups the dataset by month.

    Parameters:
        model (str): Filename of the model NetCDF file (e.g., 'CanCM4i.nc').
    """
    files = sorted(glob(os.path.join(f'Data/Models/{model}', '*.nc')))
    ds = xr.open_mfdataset(files, concat_dim='S', combine='nested', decode_times=False)
    ds = ds['prec'].mean(dim='M')
    ds = convert_precip(ds, time_dim='S')
    ds = convert_time(ds, time_dim='S')

    return ds

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

def spatial_anomaly_correlation_coefficient(model, baseline, dim='date'):
    model_anom = model - model.mean(dim=dim)
    baseline_anom = baseline - baseline.mean(dim=dim)

    numerator = (model_anom * baseline_anom).sum(dim=dim)
    model_var = (model_anom ** 2).sum(dim=dim)
    baseline_var = (baseline_anom ** 2).sum(dim=dim)

    denominator = np.sqrt(model_var * baseline_var)

    print("Model anomaly variance:", model_var.mean().values)
    print("Baseline anomaly variance:", baseline_var.mean().values)

    acc = xr.where(denominator != 0, numerator / denominator, np.nan)

    return acc


# Load baseline data
# Coordinates (x, y, date)
# Vars precip and spatial_ref
baseline_files = sorted(glob('Data/BaselineCleaned/*.nc'))
baseline_ds = xr.open_mfdataset(
    baseline_files,
    combine='nested',
    concat_dim="date"
)

# Load model data
model_ds = load_model_data(model='CanCM4i')
months = sorted(set(d[4:6] for d in baseline_ds['date'].values.astype(str)))

grouped_baseline = baseline_ds.groupby(baseline_ds['date'].str[-2:])
grouped_model = model_ds.groupby(model_ds['date'].str[-2:])

results = defaultdict(list)

# Compare model predictions with baseline data
# for l in np.arange(0.5, 12, 1):
#     print(f"Processing lead time: {l}")

for month in months:
    print(f"Processing month: {month}")

    baseline_slice = baseline_ds.sel(date=baseline_ds['date'].str[-2:] == month)
    model_slice = model_ds.sel(date=model_ds['date'].str[-2:] == month).sel(L=0.5)

    # Normalize and sort longitudes
    model_slice = model_slice.rename({'X': 'x', 'Y': 'y'})
    model_slice['x'] = ((model_slice['x'] + 180) % 360) - 180
    model_slice = model_slice.sortby('x')

    model_slice = model_slice.interp(x=baseline_slice.x, y=baseline_slice.y)

    diff = baseline_slice['precip'] - model_slice
    bias = diff.mean(dim='date')
    rmse = np.sqrt((diff ** 2).mean(dim='date'))
    acc = spatial_anomaly_correlation_coefficient(model_slice, baseline_slice)

    results[month].append({
        'lead': 0.5,
        'bias': bias,
        'rmse': rmse,
        'acc': acc
    })
