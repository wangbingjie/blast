from bokeh.models import Ellipse, LogColorMapper,ColumnDataSource
from bokeh.layouts import gridplot
from bokeh.plotting import figure
from bokeh.embed import components
from astropy.wcs import WCS
import numpy as np


def plot_image(figure, fits_image):
    image_data = fits_image[0].data
    image_data = np.nan_to_num(image_data, nan=0)#)=np.amin(image_data))
    image_data = image_data + abs(np.amin(image_data)) + 0.1
    figure.image(image=[image_data])
    color_mapper = LogColorMapper(palette='Greys256')
    figure.image(image=[image_data], x=0, y=0, dw=len(image_data), dh=len(image_data),
               color_mapper=color_mapper, level="image")
    figure.axis.visible = False
    figure.xgrid.visible = False
    figure.ygrid.visible = False

    return figure

def plot_aperture(figure, aperture):
    x, y = aperture.positions
    print(aperture.a)
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
                        plot_width=400,
                        plot_height=400)


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
