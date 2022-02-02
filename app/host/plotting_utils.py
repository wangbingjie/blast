from bokeh.models import Ellipse, LogColorMapper,ColumnDataSource, Plot, Scatter, LinearAxis,Grid
from bokeh.layouts import gridplot
from bokeh.plotting import figure
from bokeh.embed import components
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from host.host_utils import survey_list
from host.catalog_photometry import filter_information
import numpy as np
from astropy.io import fits
from bokeh.models import Circle, ColumnDataSource, Cross

def plot_image(image_data, figure):

    image_data = np.nan_to_num(image_data, nan=0)#)=np.amin(image_data))
    image_data = image_data + abs(np.amin(image_data)) + 0.1
    figure.image(image=[image_data])
    color_mapper = LogColorMapper(palette='Greys256')
    figure.image(image=[image_data], x=0, y=0, dw=len(image_data), dh=len(image_data),
               color_mapper=color_mapper, level="image")


def plot_position(object, wcs, plotting_kwargs=None, plotting_func=None):
    """
    Plot position of object on a cutout.
    """
    obj_ra, obj_dec = object.ra_deg, object.dec_deg
    sky_position = SkyCoord(ra=obj_ra, dec=obj_dec, unit='deg')
    x_pixel, y_pixel = wcs.world_to_pixel(sky_position)
    plotting_func([x_pixel], [y_pixel], **plotting_kwargs)
    return None

def plot_aperture(figure, aperture):
    x, y = aperture.positions
    source = ColumnDataSource(dict(x=[x], y=[y], w=[aperture.a], h=[aperture.b], theta=[aperture.theta]))
    glyph = Ellipse(x="x", y="y", width="w", height="h", angle="theta",
                    fill_color="#cab2d6",fill_alpha=0.1, line_color='red')
    figure.add_glyph(source, glyph)
    return figure


def plot_image_grid(image_dict, apertures=None):

    figures = []
    for survey, image in image_dict.items():
        fig = figure(title=survey,
                        x_axis_label='',
                        y_axis_label='',
                        plot_width=1000,
                        plot_height=1000)
        fig = plot_image(fig, image)
        if apertures is not None:
            aperture = apertures.get(survey)
            if aperture is not None:
                wcs = WCS(image[0].header)
                aperture = apertures[survey].to_pixel(wcs)
                fig = plot_aperture(fig, aperture)
        figures.append(fig)

    plot = gridplot(figures, ncols=3, width=400, height=400)
    script, div = components(plot)
    return {'bokeh_cutout_script': script, 'bokeh_cutout_div': div}

def plot_cutout_image(cutout=None, transient=None):

    title = cutout.filter if cutout is not None else 'No cutout selected'
    fig = figure(title=f'{title}',
                 x_axis_label='',
                 y_axis_label='',
                 plot_width=600,
                 plot_height=600)

    fig.axis.visible = False
    fig.xgrid.visible = False
    fig.ygrid.visible = False

    if cutout is not None:
        with fits.open(cutout.fits.name) as fits_file:
            image_data = fits_file[0].data
            wcs = WCS(fits_file[0].header)

        transient_kwargs = {'legend_label': f'{transient.tns_name}', 'size': 30,
                            'line_width': 2}
        plot_position(transient, wcs, plotting_kwargs=transient_kwargs,
                      plotting_func=fig.cross)
        host_kwargs = {'legend_label': f'Host: {transient.host.name}', 'size': 40,
                            'line_width': 2}
        plot_position(transient, wcs, plotting_kwargs=host_kwargs,
                      plotting_func=fig.circle)

    else:
        image_data = np.zeros((500,500))


    plot_image(image_data, fig)

    script, div = components(fig)
    return {'bokeh_cutout_script': script, 'bokeh_cutout_div': div}


def plot_catalog_sed(catalog_dict):
    """
    Plot SED from available catalog data
    """
    catalogs = survey_list('host/data/catalog_metadata.yml')
    filter_info = [filter_information(catalog) for catalog in catalogs]

    fig = figure(title='Spectral energy distribution', width=1200, height=400,
                 min_border=0, toolbar_location=None, x_axis_type="log",
                 x_axis_label="Wavelength [micro-m]", y_axis_label="Magnitude")

    wavelengths, mags, mag_errors = [], [], []

    for catalog, data in catalog_dict.items():
        filter_data = [filter for filter in filter_info
                       if filter['name'] == catalog][0]
        wavelengths.append(filter_data['WavelengthEff'] * 0.0001)
        mags.append(data['mag'])
        mag_errors.append((data['mag_error']))


    fig = plot_errorbar(fig, wavelengths, mags, yerr=mag_errors)

    #xaxis = LinearAxis()
    #figure.add_layout(xaxis, 'below')

    #yaxis = LinearAxis()
    #fig.add_layout(yaxis, 'left')

    #fig.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
    #fig.add_layout(Grid(dimension=1, ticker=yaxis.ticker))
    script, div = components(fig)
    return {'bokeh_sed_script': script, 'bokeh_sed_div': div}


def plot_errorbar(figure, x, y, xerr=None, yerr=None, color='red',
             point_kwargs={}, error_kwargs={}):
    """
    Plot data points with error bars on a bokeh plot
    """
    figure.circle(x, y, color=color, **point_kwargs)

    if xerr:
        x_err_x = []
        x_err_y = []
        for px, py, err in zip(x, y, xerr):
            x_err_x.append((px - err, px + err))
            x_err_y.append((py, py))
        figure.multi_line(x_err_x, x_err_y, color=color, **error_kwargs)

    if yerr:
        y_err_x = []
        y_err_y = []
        for px, py, err in zip(x, y, yerr):
            y_err_x.append((px, px))
            y_err_y.append((py - err, py + err))
        figure.multi_line(y_err_x, y_err_y, color=color, **error_kwargs)
    return figure

def plot_sed(figure, photometry_dict):
    """
    Plot photometry on SED
    """

