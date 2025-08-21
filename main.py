from utils.io import load_model_data, load_baseline_data
from utils.metrics import spatial_anomaly_correlation_coefficient
from utils.plotting import plot_metric_on_us_map
from collections import defaultdict
import numpy as np
import os
from joblib import dump, load

MODEL_NAME = 'CanCM4i'
LEAD_TIME = 0.5
CACHE_PATH = f'cache/{MODEL_NAME}_lead{LEAD_TIME}_metrics.joblib'

os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

if os.path.exists(CACHE_PATH):
    print(f"Loading cached results from {CACHE_PATH}...")
    results = load(CACHE_PATH)

else:
    print("No cache found. Computing metrics...")

    baseline_ds = load_baseline_data()
    model_ds = load_model_data(MODEL_NAME)

    months = sorted(set(d[4:6] for d in baseline_ds['date'].values.astype(str)))
    results = defaultdict(list)

    for month in months:
        print(f"Processing month: {month}")

        baseline_slice = baseline_ds.sel(date=baseline_ds['date'].str[-2:] == month)
        model_slice = model_ds.sel(date=model_ds['date'].str[-2:] == month).sel(L=LEAD_TIME)

        # Normalize model coords and interpolate onto baseline
        model_slice = model_slice.rename({'X': 'x', 'Y': 'y'})
        model_slice['x'] = ((model_slice['x'] + 180) % 360) - 180
        model_slice = model_slice.sortby('x')
        model_slice = model_slice.interp(x=baseline_slice.x, y=baseline_slice.y)

        # Interpolate once more to fill remaining NaNs
        model_slice = model_slice.ffill(dim='x').bfill(dim='x').ffill(dim='y').bfill(dim='y')
        baseline_slice = baseline_slice.ffill(dim='x').bfill(dim='x').ffill(dim='y').bfill(dim='y')

        # Intermediary stats used for final output stats
        baseline_max = baseline_slice['precip'].max(dim='date')
        baseline_min = baseline_slice['precip'].min(dim='date')
        baseline_range = baseline_max - baseline_min
        diff = baseline_slice['precip'] - model_slice
        baseline_mean = baseline_slice['precip'].mean(dim='date')
        model_mean = model_slice.mean(dim='date')

        bias_ratio = model_mean / baseline_mean
        rmse = np.sqrt((diff ** 2).mean(dim='date'))
        nrmse = rmse / baseline_range
        acc = spatial_anomaly_correlation_coefficient(model_slice, baseline_slice['precip'])

        # Compute monthly averages for baseline and model data
        baseline_avg = baseline_slice['precip'].mean(dim='date')
        model_avg = model_slice.mean(dim='date')

        results[month].append({
            'lead': LEAD_TIME,
            'bias_ratio': bias_ratio,
            'nrmse': nrmse,
            'acc': acc,
            'baseline_avg': baseline_avg,
            'model_avg': model_avg
        })

    # Save to cache
    print(f"Caching results to {CACHE_PATH}...")
    dump(results, CACHE_PATH)
    print("Done.")

units = {
    'baseline_avg': 'mm/month',
    'model_avg': 'mm/month',
    'bias_ratio': '',
    'acc': '',
    'nrmse': ''
}

# Generate plots
for month, metrics in results.items():
    for metric_name, metric_value in metrics[0].items():
        if metric_name != 'lead':
            unit = units.get(metric_name, '')
            title = f"{metric_name.replace('_', ' ').title()} for {month} and lead={LEAD_TIME}"
            if unit:
                title += f" ({unit})"

            plot_metric_on_us_map(
                metric_value,
                title=title,
                metric=metric_name,
                model=MODEL_NAME,
                month=month,
                lead=LEAD_TIME
            )