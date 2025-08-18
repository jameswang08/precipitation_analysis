from utils.io import load_model_data, load_baseline_data
from utils.metrics import spatial_anomaly_correlation_coefficient
from utils.plotting import plot_metric_on_us_map
from collections import defaultdict
import numpy as np

# Load data
baseline_ds = load_baseline_data()
model_ds = load_model_data('CanCM4i')

months = sorted(set(d[4:6] for d in baseline_ds['date'].values.astype(str)))
results = defaultdict(list)

for month in months:
    print(f"Processing month: {month}")

    baseline_slice = baseline_ds.sel(date=baseline_ds['date'].str[-2:] == month)
    model_slice = model_ds.sel(date=model_ds['date'].str[-2:] == month).sel(L=0.5)

    model_slice = model_slice.rename({'X': 'x', 'Y': 'y'})
    model_slice['x'] = ((model_slice['x'] + 180) % 360) - 180
    model_slice = model_slice.sortby('x')
    model_slice = model_slice.interp(x=baseline_slice.x, y=baseline_slice.y)

    diff = baseline_slice['precip'] - model_slice
    bias = diff.mean(dim='date')
    rmse = np.sqrt((diff ** 2).mean(dim='date'))
    acc = spatial_anomaly_correlation_coefficient(model_slice, baseline_slice['precip'])

    results[month].append({
        'lead': 0.5,
        'bias': bias,
        'rmse': rmse,
        'acc': acc
    })

# Example plot
plot_metric_on_us_map(
    results['01'][0]['acc'],
    title='ACC for January (Lead=0.5)',
    cmap='RdBu_r'
)
