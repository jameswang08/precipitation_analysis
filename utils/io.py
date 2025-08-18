import xarray as xr
import os
from glob import glob
from .processing import convert_precip, convert_time

def load_model_data(model: str) -> xr.DataArray:
    files = sorted(glob(os.path.join(f'Data/Models/{model}', '*.nc')))
    ds = xr.open_mfdataset(files, concat_dim='S', combine='nested', decode_times=False)
    ds = ds['prec'].mean(dim='M')
    ds = convert_precip(ds, time_dim='S')
    ds = convert_time(ds, time_dim='S')
    return ds

def load_baseline_data() -> xr.Dataset:
    files = sorted(glob('Data/BaselineCleaned/*.nc'))
    ds = xr.open_mfdataset(files, combine='nested', concat_dim="date")
    return ds
