import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import xarray as xr

def plot_metric_on_us_map(data: xr.DataArray, title: str, cmap='RdBu_r'):
    plt.figure(figsize=(12, 8))
    ax = plt.axes(projection=ccrs.LambertConformal())
    ax.set_extent([-125, -66.5, 24, 50], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linestyle=':')

    vmin = np.nanpercentile(data, 5)
    vmax = np.nanpercentile(data, 95)

    img = ax.pcolormesh(
        data['x'], data['y'], data,
        cmap=cmap, vmin=vmin, vmax=vmax,
        transform=ccrs.PlateCarree()
    )

    plt.title(title, fontsize=16)
    cb = plt.colorbar(img, ax=ax, orientation='vertical', shrink=0.7, pad=0.02)
    cb.set_label(title)
    plt.show()
