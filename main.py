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

        model_slice = model_slice.rename({'X': 'x', 'Y': 'y'})
        model_slice['x'] = ((model_slice['x'] + 180) % 360) - 180
        model_slice = model_slice.sortby('x')
        model_slice = model_slice.interp(x=baseline_slice.x, y=baseline_slice.y)

        diff = baseline_slice['precip'] - model_slice
        bias = diff.mean(dim='date')
        rmse = np.sqrt((diff ** 2).mean(dim='date'))
        acc = spatial_anomaly_correlation_coefficient(model_slice, baseline_slice['precip'])

        results[month].append({
            'lead': LEAD_TIME,
            'bias': bias,
            'rmse': rmse,
            'acc': acc
        })

    # Save to cache
    print(f"Caching results to {CACHE_PATH}...")
    dump(results, CACHE_PATH)
    print("Done.")

# --- Example Plot ---
plot_metric_on_us_map(
    results['01'][0]['acc'],
    title='ACC for January (Lead=0.5)',
    cmap='RdBu_r'
)
