import xarray as xr
import numpy as np

def spatial_anomaly_correlation_coefficient(model, baseline, dim='date'):
    return xr.corr(baseline, model, dim=dim)

def normalized_root_mean_square_error(difference, average, dim='year'):
    rmse = np.sqrt(((difference) ** 2).mean(dim=dim))
    return rmse / (average + 1e-10)

def normalized_mean_absolute_difference(difference, average, dim='year'):
    mad = (np.abs(difference)).mean(dim=dim)
    return mad / (average + 1e-10)
