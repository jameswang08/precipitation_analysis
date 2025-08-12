# Script to convert bil files into NetCDF format for future processing.

import os
from glob import glob
import rioxarray as rxr # type: ignore
import xarray as xr # type: ignore

root = 'Data/Baseline'
output_dir = 'Data/BaselineCleaned'
years = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]

for year in years:
    year_path = os.path.join(root, year)
    bil_files = glob(os.path.join(year_path, '*.bil'))

    print(f"Processing {year}, found {len(bil_files)} bil files.")

    for bil_file in bil_files:

        # Assuming file structure like PRISM_ppt_stable_4kmM3_2018_all_bil where time is 4th element
        filename = os.path.basename(bil_file)
        file_date = filename.split('_')[4]

        if len(file_date) != 6:
            print(f"Skipping year summary file: {filename}")
            continue

        print(f"Processing {bil_file}")

        ds = rxr.open_rasterio(bil_file)
        ds.name = 'precipitation'

        precip = ds.squeeze('band')
        ds_clean = precip.to_dataset(name='precip')

        # Add date as a coordinate (string) to the dataset
        ds_clean = ds_clean.assign_coords(date=file_date)

        final_nc = os.path.join(output_dir, f"{file_date}.nc")
        ds_clean.to_netcdf(final_nc)

        print(f"Saved processed NetCDF to {final_nc}")
