import xarray as xr
import pandas as pd
import calendar
from typing import Union

def convert_precip(ds: xr.DataArray, time_dim='S') -> xr.DataArray:
    months_since_1960 = ds[time_dim].values
    ref_date = pd.Timestamp("1960-01-01")
    dates = pd.to_datetime([ref_date + pd.DateOffset(months=int(m)) for m in months_since_1960])
    days_in_month = [calendar.monthrange(d.year, d.month)[1] for d in dates]
    days_da = xr.DataArray(days_in_month, dims=[time_dim], coords={time_dim: ds[time_dim]})
    return ds * days_da

def convert_time(ds: xr.Dataset | xr.DataArray, time_dim='S') -> Union[xr.DataArray, xr.Dataset]:
    months_since_1960 = ds[time_dim].values
    ref_date = pd.Timestamp("1960-01-01")
    dates = pd.to_datetime([ref_date + pd.DateOffset(months=int(m)) for m in months_since_1960])
    yyyymm = dates.strftime('%Y%m')
    ds = ds.assign_coords(date=(time_dim, yyyymm))
    ds = ds.swap_dims({time_dim: "date"})
    ds = ds.drop_vars(time_dim)
    return ds

def calculate_baseline(date: str, lead: float) -> str:
    year = int(date[:4])
    month = int(date[4:6]) + int(lead)
    if month > 12:
        year += 1
        month -= 11
    return f"{year}{month:02d}"
