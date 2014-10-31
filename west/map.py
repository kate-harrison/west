import matplotlib.pyplot as plt
import matplotlib.cm
import numpy
import datetime
from custom_logging import getModuleLogger
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


class Map(object):
    """
    Plots an image of the given :class:`data_map.DataMap2D`.
    """
    title_font_size = 20
    fontname = "Bitstream Vera Sans"
    colorbar_font_size = 16

    _label_num_decimals = 1

    _default_boundary_color = 'k'
    _default_boundary_linewidth = 5

    def _transformation_linear(data):
        return data

    def _transformation_log(data, base=6):
        return numpy.log1p(data) / numpy.log(base)

    def _transformation_inverse_log(data, base=6):
        return numpy.expm1(data * numpy.log(base))

    def _transformation_atan(data, scale=20):
        return numpy.arctan(data / scale) / (numpy.pi / 2)

    def _transformation_inverse_atan(data, scale=20):
        return numpy.tan(data * (numpy.pi / 2)) * scale

    _transformation_dict = {"linear": _transformation_linear,
                            "log": _transformation_log,
                            "atan": _transformation_atan}
    _transformation_inverse_dict = {"linear": _transformation_linear,
                                    "log": _transformation_inverse_log,
                                    "atan": _transformation_inverse_atan}


    def get_transformation(self, transformation_type):
        if transformation_type in self._transformation_dict:
            return self._transformation_dict[transformation_type]
        else:
            self.log.warning("Defaulting to linear transformation")
            return Map._transformation_linear

    def get_transformation_inverse(self, transformation_type):
        if transformation_type in self._transformation_inverse_dict:
            return self._transformation_inverse_dict[transformation_type]
        else:
            self.log.warning("Defaulting to linear transformation for inverse")
            return Map._transformation_linear

    def __init__(self, datamap2d, transformation="linear",
                 is_in_region_map=None):
        """
        Plots an image of the given :class:`data_map.DataMap2D`.

        :param datamap2d:
        :type datamap2d: :class:`data_map.DataMap2D`
        :param transformation: the transformation to be applied to the data \
                before plotting ("linear", "log", or "atan")
        :type transformation: string
        :return: None
        """
        self.log = getModuleLogger(self)

        self._transformation = self.get_transformation(transformation)
        self._transformation_inverse = self.get_transformation_inverse(
            transformation)
        self.log.debug("Using transformation %s" % str(self._transformation))

        self._datamap2d = datamap2d
        self._data = self._transformation(datamap2d.mutable_matrix)
        self.make_region_background_white(is_in_region_map)

        self._fig, self._ax = plt.subplots()
        self._canvas = FigureCanvas(self._fig)
        self._image = self._ax.imshow(self._data, origin="lower")
        self._image.set_interpolation('nearest')

        self._remove_axes()
        self._configure_colors()
        self._fig.set_facecolor('white')

        self._boundary_plots = []
        self.set_boundary_color()
        self.set_boundary_linewidth()

        self._colorbar = None

    def make_region_background_white(self, is_in_region_map):
        """
        Sets the value for locations outside the region such that they will
        be plotted as white.

        .. warning:: Not implemented yet.

        :param is_in_region_map: map indicating which locations are in the \
                region (1 = in region; 0 = not in region)
        :type: :class:`data_map.DataMap2D`
        :return: None
        """
        if is_in_region_map is None:
            self.log.debug(
                "Cannot make region background white: no region map provided")
            return

        from data_map import DataMap2D

        if not isinstance(is_in_region_map, DataMap2D):
            raise TypeError(
                "Expected the second argument to be of type DataMap2D")

        import numpy.ma as ma

        mask = 1.0 - is_in_region_map.get_matrix_copy()
        self._data = ma.masked_array(self._data, mask=mask)

    def set_data_max_value(self, threshold=None):
        """
        Clamps values above the threshold at the threshold. This prevents
        out-of-bounds values from being plotted as white due to the colormap.

        .. warning:: Not implemented yet.

        :param threshold: maximum value for the data
        :type threshold: float
        :return: None
        """
        # TODO: write this function
        # Tip: use http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html
        return

    def auto_clip_data(self, threshold=0.98):
        """
        Clamps values above the threshold at the threshold. This prevents
        out-of-bounds values from being plotted as white due to the colormap.

        :param threshold: value in [0, 1] specifying the fraction of the \
                actual maximum to use as the threshold
        :type threshold: float
        :return: None
        """
        data_max = self._data.max()
        self.set_data_max_value(threshold * data_max)

    def save(self, filename=None):
        """
        Save the plot as a file (*.png).

        :param filename: destination filename (including extension)
        :type filename: str
        :return: None
        """
        filename = filename or (str(datetime.datetime.utcnow()) + ".png")
        self.log.debug("Saving to filename %s" % filename)
        self._canvas.print_png(filename)  # also accepts dpi= kwarg

    def _remove_axes(self):
        """
        Remove the axes from the plot.
        """
        self._ax.get_xaxis().set_visible(False)
        self._ax.get_yaxis().set_visible(False)
        self._ax.axis('off')

    def remove_colorbar(self):
        """
        Remove the colorbar from the plot.
        """
        self._fig.delaxes(self._fig.axes[1])

    def _configure_colors(self):
        """
        Set up the colors for the plot.
        """
        self._set_colormap()
        self._set_clim()

    def _set_colormap(self):
        """
        Sets the colormap to jet. Values that exceed the colormap's values
        will be plotted as white. Those that are below the minimum will be
        plotted as black. "Bad" values (e.g. NaN) will be plotted as white.
        """
        cmap = matplotlib.cm.jet
        cmap.set_under('k')
        cmap.set_over('w')
        cmap.set_bad('w')
        self._image.set_cmap(cmap)

    def _set_clim(self, vmin=None, vmax=None):
        """
        Sets the limits of the colormap.
        """
        if vmin is not None:
            vmin = self._transformation(vmin)
        else:
            vmin = 0
        if vmax is not None:
            vmax = self._transformation(vmax)
        else:
            vmax = numpy.max(self._data) * 1.01
        self._image.set_clim(vmin, vmax)

        return vmin, vmax

    def add_colorbar(self, vmin=None, vmax=None, label=None,
                     decimal_precision=None):
        """
        Add a colorbar to the plot.

        :param vmin: minimum value for the colorbar
        :param vmax: maximum value for the colorbar
        :param label: label for the colorbar
        :param decimal_precision:
        :return: None
        """
        self._colorbar = self._fig.colorbar(self._image)

        (vmin, vmax) = self._set_clim(vmin, vmax)

        if decimal_precision is not None:
            self._label_num_decimals = decimal_precision

        if label is not None:
            self.set_colorbar_label(label)

        self._colorbar.ax.tick_params(labelsize=self.colorbar_font_size)

        max_caxis_transformed = vmax
        max_caxis = self._transformation_inverse(max_caxis_transformed)
        self.set_colorbar_ticks(max_caxis)

    def set_colorbar_ticks(self, locations, labels=None):
        """
        Set specific ticks to be shown on the colorbar. Locations should be
        given in the same units as the original data regardless of any
        transformation of the data done during mapping.

        If `locations` is a scalar, 10 linearly spaced labels will be
        auto-generated between 0 and `locations`.

        :param locations: list of values at which to place the ticks
        :type locations: list of floats
        :param labels: labels corresponding to the locations
        :type labels: list of strs
        :return: None
        """
        # Assume that locations and labels are in *original* data coordinates
        # Generate list of locations if only one given
        # Note: need to transform to plot space first
        # In this mode, the input 'labels' is ignored
        if not isinstance(locations, list):
            max_transformed_location = self._transformation(locations)
            transformed_locations_temp = numpy.linspace(0,
                                                        max_transformed_location,
                                                        11)
            locations = self._transformation_inverse(transformed_locations_temp)
            labels = None

        if labels is None:
            # Round label locations
            if self._label_num_decimals > 0:
                locations = numpy.round(locations, self._label_num_decimals)
            else:
                locations = [int(l) for l in locations]
            # Create the label strings
            labels = [str(l) for l in locations]

        transformed_locations = self._transformation(locations)

        self._colorbar.set_ticks(transformed_locations)
        self._colorbar.set_ticklabels(labels)

    def set_number_of_colorbar_ticks(self, num_ticks):
        """
        Set the number of ticks to be shown on the colorbar.
        """
        (min_val, max_val) = self._colorbar.get_clim()
        tick_locations = numpy.linspace(min_val, max_val, num_ticks)
        self.set_colorbar_ticks(tick_locations)

    def blocking_show(self):
        """
        Display the plot, which is a blocking action.
        """
        plt.show()

    def set_colorbar_label(self, label):
        """
        Label the colorbar with the given `label` string.
        """
        if self._colorbar is None:
            self.add_colorbar()
        self._colorbar.set_label(label, fontsize=self.colorbar_font_size,
                                 fontname=self.fontname)

    def set_title(self, title):
        """
        Set the title of the plot with the given `title` string. Returns a
        handle to the title object.
        """
        return plt.title(title, fontsize=self.title_font_size,
                         fontname=self.fontname)

    def set_boundary_color(self, new_color=None):
        """
        Set the color of the boundary line. See :meth:`add_boundary_outlines` and
        http://matplotlib.org/api/artist_api.html#matplotlib.patches.Patch.set_color
        for more details.
        """
        self._boundary_color = new_color or self._default_boundary_color

        # Update color if the boundary is already plotted
        for plot in self._boundary_plots:
            plot.set_color(self._boundary_color)

    def set_boundary_linewidth(self, new_linewidth=None):
        """
        Set the width of the boundary line. See :meth:`add_boundary_outlines` and
        http://matplotlib.org/api/artist_api.html#matplotlib.lines.Line2D.set_linewidth
        for more details.
        """
        self._boundary_linewidth = new_linewidth or self._default_boundary_linewidth

        # Update color if the boundary is already plotted
        for plot in self._boundary_plots:
            plot.set_linewidth(self._boundary_linewidth)

    def add_boundary_outlines(self, boundary):
        """
        Add the specified boundary (a :class:`boundary.Boundary` object) to
        the plot as an outline. Color and linewidth can be customized via
        :meth:`set_boundary_color` and :meth:`set_boundary_linewidth`.
        """
        color = self._boundary_color
        linewidth = self._boundary_linewidth

        map_min_lat = min(self._datamap2d.latitudes)
        map_max_lat = max(self._datamap2d.latitudes)
        map_min_lon = min(self._datamap2d.longitudes)
        map_max_lon = max(self._datamap2d.longitudes)

        num_lat_divs = len(self._datamap2d.latitudes)
        num_lon_divs = len(self._datamap2d.longitudes)

        def change_range(old_value, old_min, old_max, new_min, new_max):
            return (((old_value - old_min) * (new_max - new_min)) / (
            old_max - old_min)) + new_min

        for (lats, lons) in boundary.get_sets_of_exterior_coordinates():
            new_lats = change_range(lats, map_min_lat, map_max_lat, 0,
                                    num_lat_divs - 1)
            new_lons = change_range(lons, map_min_lon, map_max_lon, 0,
                                    num_lon_divs - 1)

            new_plot = self._ax.plot(new_lons, new_lats, color,
                                     linewidth=linewidth)
            self._boundary_plots.append(new_plot[0])

        self._ax.axis([0, num_lon_divs - 1, 0, num_lat_divs - 1])
