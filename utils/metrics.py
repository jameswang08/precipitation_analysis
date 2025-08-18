import xarray as xr
import numpy as np

def spatial_anomaly_correlation_coefficient(model, baseline, dim='date'):
    model_anom = model - model.mean(dim=dim)
    baseline_anom = baseline - baseline.mean(dim=dim)

    numerator = (model_anom * baseline_anom).sum(dim=dim)
    denominator = np.sqrt((model_anom ** 2).sum(dim=dim) * (baseline_anom ** 2).sum(dim=dim))

    acc = xr.where(denominator != 0, numerator / denominator, np.nan)
    return acc
