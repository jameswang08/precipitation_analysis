import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import xarray as xr
import regionmask
import geopandas as gpd

def plot_metric_on_us_map(data: xr.DataArray, title: str, cmap='RdBu_r'):
    # Load Natural Earth admin-0 countries via geopandas
    world = gpd.read_file('Data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp')
    us_shape = world[world['ADMIN'] == 'United States of America'].geometry.values[0]

    # Create a regionmask from the US polygon
    mask = regionmask.Regions([us_shape], names=['US'], abbrevs=['US'])
    
    # Create the mask over the data grid
    us_mask = mask.mask(data['x'], data['y'])
    
    # Apply mask: set non-US values to NaN
    data_us_only = data.where(us_mask == 0)

    # Plotting
    plt.figure(figsize=(12, 8))
    ax = plt.axes(projection=ccrs.LambertConformal())
    ax.set_extent([-125, -66.5, 24, 50], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linestyle=':')

    vmin = np.nanpercentile(data_us_only, 5)
    vmax = np.nanpercentile(data_us_only, 95)

    img = ax.pcolormesh(
        data['x'], data['y'], data_us_only,
        cmap=cmap, vmin=vmin, vmax=vmax,
        transform=ccrs.PlateCarree()
    )

    plt.title(title, fontsize=16)
    cb = plt.colorbar(img, ax=ax, orientation='vertical', shrink=0.7, pad=0.02)
    cb.set_label(title)
    plt.show()
