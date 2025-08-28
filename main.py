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

    results = defaultdict(list)

    # month_groups = [
    #     (1, 2, 3),
    #     (4, 5, 6),
    #     (7, 8, 9),
    #     (10, 11, 12)
    # ]

    # month_map = {
    #     (1, 2, 3): "Jan-Mar",
    #     (4, 5, 6): "Apr-Jun",
    #     (7, 8, 9): "Jul-Sep",
    #     (10, 11, 12): "Oct-Dec"
    # }

    month_groups = [(m,) for m in range(1, 13)]

    month_map = {
        (1,): "January",
        (2,): "February",
        (3,): "March",
        (4,): "April",
        (5,): "May",
        (6,): "June",
        (7,): "July",
        (8,): "August",
        (9,): "September",
        (10,): "October",
        (11,): "November",
        (12,): "December"
    }

    for group in month_groups:
        print(f"Processing months: {group}")

        baseline_group = baseline_ds.where(baseline_ds['date'].dt.month.isin(group), drop=True)
        model_group = model_ds.where(model_ds['date'].dt.month.isin(group), drop=True).sel(L=LEAD_TIME)

        baseline_slice = baseline_group.groupby('date.year').mean(dim='date')
        model_slice = model_group.groupby('date.year').mean(dim='date')


        # Interpolate once more to fill remaining NaNs
        baseline_slice = baseline_slice.ffill(dim='x').bfill(dim='x').ffill(dim='y').bfill(dim='y')

        # Interpolate onto model grid
        baseline_slice = baseline_slice.interp(x=model_slice.x, y=model_slice.y)

        # Intermediary stats used for final output stats
        baseline_max = baseline_slice['precip'].max(dim='year')
        baseline_min = baseline_slice['precip'].min(dim='year')
        baseline_range = baseline_max - baseline_min
        diff = baseline_slice['precip'] - model_slice
        baseline_mean = baseline_slice['precip'].mean(dim='year')
        model_mean = model_slice.mean(dim='year')

        bias_ratio = model_mean / baseline_mean
        rmse = np.sqrt((diff ** 2).mean(dim='year'))
        nrmse = rmse / baseline_range
        acc = spatial_anomaly_correlation_coefficient(model_slice, baseline_slice['precip'], "year")

        # Compute monthly averages for baseline and model data
        baseline_avg = baseline_slice['precip'].mean(dim='year')
        model_avg = model_slice.mean(dim='year')

        results[month_map[group]].append({
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
for group, metrics in results.items():
    for metric_name, metric_value in metrics[0].items():
        if metric_name != 'lead':
            unit = units.get(metric_name, '')
            title = f"{metric_name.replace('_', ' ').title()} for {group}"
            if metric_name == "baseline_avg":
                title = "PRISM " + title
            else:
                title = MODEL_NAME + " " + title + f" with lead={LEAD_TIME}"
            if unit:
                title += f" ({unit})"

            plot_metric_on_us_map(
                metric_value,
                title=title,
                metric=metric_name,
                model=MODEL_NAME,
                month=group,
                lead=LEAD_TIME
            )