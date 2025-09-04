from utils.io import load_model_data, load_baseline_data
from utils.metrics import spatial_anomaly_correlation_coefficient
from utils.plotting import plot_metric_on_us_map
import numpy as np
import argparse
import os
from joblib import dump, load

parser = argparse.ArgumentParser(description="Process model parameters.")
parser.add_argument('region', type=str, help='Region name')
parser.add_argument('model', type=str, help='Model name')
parser.add_argument('lead_time', type=float, help='Lead time')
parser.add_argument('time_scale', type=str, help='Time scale')
parser.add_argument('month', type=str, help='Month or season')
args = parser.parse_args()

REGION = args.region
MODEL_NAME = args.model
LEAD_TIME = args.lead_time
TIME_SCALE = args.time_scale
MONTH = args.month

if TIME_SCALE.lower() == 'seasonal':
    CACHE_PATH = f'cache/{MODEL_NAME}_seasonal_lead{LEAD_TIME}_metrics.joblib'
else:
    CACHE_PATH = f'cache/{MODEL_NAME}_lead{LEAD_TIME}_metrics.joblib'

os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

if os.path.exists(CACHE_PATH):
    print(f"Loading cached results from {CACHE_PATH}...")
    results = load(CACHE_PATH)

else:
    print("No cache found. Computing metrics...")

    baseline_ds = load_baseline_data()
    model_ds = load_model_data(MODEL_NAME)

    results = {}

    if TIME_SCALE.lower() == 'seasonal':
        month_groups = [
            (1, 2, 3),
            (4, 5, 6),
            (7, 8, 9),
            (10, 11, 12)
        ]

        month_map = {
            (1, 2, 3): "Jan-Mar",
            (4, 5, 6): "Apr-Jun",
            (7, 8, 9): "Jul-Sep",
            (10, 11, 12): "Oct-Dec"
        }

    else:
        month_groups = [(m,) for m in range(1, 13)]

        month_map = {
            (1,): "Jan",
            (2,): "Feb",
            (3,): "Mar",
            (4,): "Apr",
            (5,): "May",
            (6,): "Jun",
            (7,): "Jul",
            (8,): "Aug",
            (9,): "Sep",
            (10,): "Oct",
            (11,): "Nov",
            (12,): "Dec"
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

        print(month_map[group])

        results[month_map[group]] = {
            'lead': LEAD_TIME,
            'bias_ratio': bias_ratio,
            'nrmse': nrmse,
            'acc': acc,
            'baseline_avg': baseline_avg,
            'model_avg': model_avg
        }

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

print("test1")
print(MONTH)
print(results.keys())

# Generate plots
for metric_name, metric_value in results[MONTH].items():
    print(f"Processing metric: {metric_name}")

    filename = f"US_{MODEL_NAME}_{MONTH}_lead{LEAD_TIME}_{metric_name}.png"
    filepath = os.path.join('./images', filename)

    if os.path.exists(filepath):
        print(f"Skipping plot generation for {filename} (already exists).")
        print(f"::PLOT::{os.path.abspath(filepath)}")
        continue

    if metric_name != 'lead':
        unit = units.get(metric_name, '')
        title = f"{metric_name.replace('_', ' ').title()} for {MONTH}"
        if metric_name == "baseline_avg":
            title = "PRISM " + title
        else:
            title = MODEL_NAME + " " + title + f" with lead={LEAD_TIME}"
        if unit:
            title += f" ({unit})"

        print(f"Calling plot_metric_on_us_map for {metric_name}")
        plot_metric_on_us_map(
            metric_value,
            title=title,
            metric=metric_name,
            model=MODEL_NAME,
            month=MONTH,
            lead=LEAD_TIME
        )