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

def spatial_anomaly_correlation_coefficient(model, baseline, dim='date'):
    model_anom = model - model.mean(dim=dim)
    baseline_anom = baseline - baseline.mean(dim=dim)

    numerator = (model_anom * baseline_anom).sum(dim=dim)
    model_var = (model_anom ** 2).sum(dim=dim)
    baseline_var = (baseline_anom ** 2).sum(dim=dim)

    denominator = np.sqrt(model_var * baseline_var)

    acc = xr.where(denominator != 0, numerator / denominator, np.nan)

    return acc


# Load baseline data
# Coordinates (x, y, date)
# Vars precip and spatial_ref
baseline_files = sorted(glob('Data/BaselineCleaned/*.nc'))
baseline_ds = xr.open_mfdataset(
    baseline_files,
    combine='nested',
    concat_dim='file_index',
    coords='minimal',
    data_vars='minimal',
    compat='override'
)
print(baseline_ds.dims)
print(baseline_ds.coords)


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
    model_slice = model_slice.rename({'X': 'x', 'Y': 'y'})
    # Normalize and sort longitudes
    model_slice['x'] = ((model_slice['x'] + 180) % 360) - 180
    model_slice = model_slice.sortby('x')
    model_slice = model_slice.interp(x=baseline_slice.x, y=baseline_slice.y)



    diff = baseline_slice['precip'] - model_slice

    bias = diff.mean(dim='date')
    rmse = np.sqrt((diff ** 2).mean(dim='date'))

    acc = spatial_anomaly_correlation_coefficient(model_slice, baseline_slice)

    # Store results
    results[month].append({
        'lead': 0.5,
        'bias': bias,
        'rmse': rmse,
        'acc': acc
    })

def overlay_results(results: Dict[str, list], output_dir: str = "output_maps"):
    """
    Plot and overlay bias, RMSE, and ACC results on a US map for each month.

    Parameters:
        results (Dict[str, list]): Dictionary with month keys and list of result dicts per month.
        output_dir (str): Directory where maps will be saved.
    """
    import xarray as xr  # Just to be safe that xr is in scope


    os.makedirs(output_dir, exist_ok=True)

    for month, stat_list in results.items():
        for stats in stat_list:
            lead = stats['lead']
            for stat_name in ['bias', 'rmse', 'acc']:
                stat_data = stats[stat_name]
                # If stat_data is Dataset, select the first variable to plot
                if isinstance(stat_data, xr.Dataset):
                    var_name = list(stat_data.data_vars)[0]
                    stat_data = stat_data[var_name]

                print(f"--- Plotting {stat_name.upper()} for month {month} lead {lead} ---")
                print(f"Data shape: {stat_data.shape}")
                print(f"Data dims: {stat_data.dims}")
                print(f"Data type: {type(stat_data)}")
                print(f"Min: {stat_data.min().values}")
                print(f"Max: {stat_data.max().values}")
                print(f"NaNs present: {stat_data.isnull().any().compute().item()}")

                fig = plt.figure(figsize=(10, 6))
                ax = plt.axes(projection=ccrs.PlateCarree())

                # Add map features
                ax.add_feature(cfeature.COASTLINE)
                ax.add_feature(cfeature.BORDERS, linestyle=':')
                ax.add_feature(cfeature.STATES, linestyle=':')

                # Plot data
                im = stat_data.plot(
                    ax=ax,
                    transform=ccrs.PlateCarree(),
                    cmap='coolwarm' if stat_name != 'acc' else 'viridis',
                    cbar_kwargs={'label': stat_name.upper()},
                    robust=True
                )

                ax.set_title(f"{stat_name.upper()} - Month: {calendar.month_name[int(month)]}, Lead: {lead}")
                ax.set_extent([-125, -66.5, 24, 50], crs=ccrs.PlateCarree())  # Focus on continental US

                # Save figure
                save_path = os.path.join(output_dir, f"{stat_name}_{month}_lead{lead:.1f}.png")
                plt.savefig(save_path, bbox_inches='tight')
                plt.close(fig)



overlay_results(results)