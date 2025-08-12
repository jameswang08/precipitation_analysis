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

def convert_time(ds: xr.Dataset | xr.DataArray, time_dim='time') -> Union[xr.DataArray, xr.Dataset]:
    """
    Convert time from months since Jan 1960 to YYYYMM format then group by month.
    """
    # Convert time coordinate to YYYYMM strings
    months_since_1960 = ds[time_dim].values
    ref_date = pd.Timestamp("1960-01-01")
    dates = pd.to_datetime([ref_date + pd.DateOffset(months=int(m)) for m in months_since_1960])
    yyyymm = dates.strftime('%Y%m')

    # Create a DataArray with YYYYMM labels as coordinate
    ds_with_yyyymm = ds.assign_coords({time_dim: yyyymm})

    return ds_with_yyyymm

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

    model_slice = model_slice.compute() if hasattr(model_slice, 'compute') else model_slice

    model_interp = model_slice.interp(
        x=baseline_slice.x,
        y=baseline_slice.y
    )
    diff = model_interp - baseline_slice['precip']

    bias = diff.mean().item()
    rmse = np.sqrt((diff ** 2).mean()).item()

    return bias, rmse

def plot_metrics_heatmaps(results):
    """
    Plot heatmaps of bias_ratio and RMSE from results dict.

    Parameters:
        results (dict): keys are date strings (YYYYMM),
                        values are lists of dicts with 'lead', 'bias_ratio', 'rmse'.
    """
    dates = sorted(results.keys())
    leads = sorted({entry['lead'] for month in results.values() for entry in month})

    # Prepare DataFrames for bias_ratio and rmse
    bias_df = pd.DataFrame(index=dates, columns=leads, dtype=float)
    rmse_df = pd.DataFrame(index=dates, columns=leads, dtype=float)

    for date in dates:
        for entry in results[date]:
            lead = entry['lead']
            bias_df.loc[date, lead] = entry['bias_ratio']
            rmse_df.loc[date, lead] = entry['rmse']

    # Convert index to datetime, format to YYYYMM string for neat labels
    bias_df.index = pd.to_datetime(bias_df.index, format='%Y%m')
    rmse_df.index = pd.to_datetime(rmse_df.index, format='%Y%m')

    # Format index as YYYYMM string (to avoid overly precise dates)
    bias_df.index = bias_df.index.strftime('%Y%m')
    rmse_df.index = rmse_df.index.strftime('%Y%m')

    # Plot side by side
    fig, axs = plt.subplots(1, 2, figsize=(16, 8))

    sns.heatmap(bias_df, cmap='coolwarm', center=0, annot=True, fmt=".2f", ax=axs[0])
    axs[0].set_title('Bias Ratio Heatmap')
    axs[0].set_xlabel('Lead Time (months)')
    axs[0].set_ylabel('Date (YYYYMM)')

    sns.heatmap(rmse_df, cmap='coolwarm', annot=True, fmt=".2f", ax=axs[1])
    axs[1].set_title('RMSE Heatmap')
    axs[1].set_xlabel('Lead Time (months)')
    axs[1].set_ylabel('Date (YYYYMM)')

    plt.tight_layout()
    plt.show()

# Store baseline data keyed by time
# Dimensions (y, x)
# Vars precip and spatial_ref
baseline_files = sorted(glob('Data/BaselineCleaned/*.nc'))
baseline_ds = xr.open_mfdataset(
    baseline_files,
    combine='nested',
    concat_dim='date',
    preprocess=lambda ds: ds.expand_dims('date')
)

# # Load model data
# grouped_ds = load_model_data(model='CanCM4i')

# # Compare model predictions with baseline data
# results = defaultdict(list)
# years = sorted(set(date[:4] for date in grouped_ds.keys()))
# months = sorted(set(date[4:6] for date in grouped_ds.keys()))

# for l in np.arange(0.5, 12, 1):
#     print(f"Processing lead time: {l}")
#     for month in months:
#         print(f"Processing month: {month}")

# plot_metrics_heatmaps(results)

# ds = load_model_data(model='CanCM4i')
ds = xr.open_dataset('Data/BaselineCleaned/201801.nc')

print(ds)