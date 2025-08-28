import xarray as xr
import pandas as pd
import os
from glob import glob
from .processing import convert_precip, convert_time
from typing import Union

def load_model_data(model: str) -> Union[xr.DataArray, xr.Dataset]:
    files = sorted(glob(os.path.join(f'Data/Models/{model}', '*.nc')))
    ds = xr.open_mfdataset(files, concat_dim='S', combine='nested', decode_times=False)
    ds = ds['prec'].mean(dim='M')
    ds = convert_precip(ds, time_dim='S')
    ds = convert_time(ds, time_dim='S')

    # Convert date to dt obj for simpler processing
    ds['date'] = pd.to_datetime(ds['date'].values, format='%Y%m')

    # Normalize model coords
    ds = ds.rename({'X': 'x', 'Y': 'y'})
    ds['x'] = ((ds['x'] + 180) % 360) - 180
    ds = ds.sortby('x')
    return ds

def load_baseline_data() -> xr.Dataset:
    files = sorted(glob('Data/BaselineCleaned/*.nc'))
    ds = xr.open_mfdataset(files, combine='nested', concat_dim="date")
    ds['date'] = pd.to_datetime(ds['date'].values, format='%Y%m')
    return ds
