# Ignoring all imports as they are installed via venv
import xarray as xr # type: ignore
import rioxarray as rxr #type: ignore
import os

# Libraries for plotting
import matplotlib.pyplot as plt # type: ignore
import cartopy.crs as ccrs # type: ignore
import cartopy.feature as cfeature # type: ignore

# Load data and aggregate models
# ds = xr.open_dataset('Data/Models/CanCM4i/2018.nc', decode_times=False)
# ds = ds['prec'].mean(dim='M')

# prec_slice = ds.isel(S=0, L=0)

# bil_file = 'Data/Baseline/PRISM_ppt_stable_4kmM3_2018_all_bil/PRISM_ppt_stable_4kmM3_2018_bil.bil'
# output_netcdf = 'Data/file.nc'

# ds = rxr.open_rasterio(bil_file)
# ds.to_netcdf(output_netcdf)

ds = xr.open_dataset('Data/file.nc')
ds = ds.rename({'__xarray_dataarray_variable__': 'precipitation'})

# print(list(ds.data_vars))
# print(ds.dims)        # Dimensions and their sizes
# print(ds.coords)

precip = ds['precipitation']
print(precip)
precip = precip.squeeze('band')
print(precip.dims)  # Should now be ('y', 'x')
import matplotlib.pyplot as plt

precip.plot()  # or if squeezed, just precip.plot()
plt.show()
