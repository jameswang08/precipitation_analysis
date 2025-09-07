import xarray as xr
import pandas as pd
import calendar
import math
from typing import Union
from dateutil.relativedelta import relativedelta

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

def clip_baseline(baseline: xr.Dataset | xr.DataArray, lead_time: int, start_year: int = 1981, end_year: int = 2018) -> Union[xr.DataArray, xr.Dataset]:
    timedelta = math.floor(lead_time)
    new_dates = [pd.Timestamp(dt) - relativedelta(months=timedelta) for dt in baseline['date'].values]
    baseline = baseline.assign_coords(date=new_dates)

    years = baseline['date'].dt.year
    mask = (years >= start_year) & (years <= end_year)
    baseline = baseline.sel(date=mask)

    return baseline
