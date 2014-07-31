import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy
from region import Region
import datetime
from custom_logging import getModuleLogger
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas




class Map(object):
    """
    Plots a map of the given matrix.
    """
    title_font_size = 20
    fontname = "Bitstream Vera Sans"    # Computer Modern is not installed
    colorbar_font_size = 16

    _label_num_decimals = 1
    _use_region_outlines = True

    _no_region_background = True

    def _transformation_linear(data):
        return data

    def _transformation_log(data, base=6):
        return numpy.log1p(data) / numpy.log(base)

    def _transformation_inverse_log(data, base=6):
        return numpy.expm1(data * numpy.log(base))

    def _transformation_atan(data, scale=20):
        return numpy.arctan( data / scale) / (numpy.pi / 2)

    def _transformation_inverse_atan(data, scale=20):
        return numpy.tan( data * (numpy.pi / 2)) * scale

    _transformation_dict = { "linear":  _transformation_linear,
                             "log":     _transformation_log,
                             "atan":    _transformation_atan}
    _transformation_inverse_dict = { "linear":  _transformation_linear,
                                     "log":     _transformation_inverse_log,
                                     "atan":    _transformation_inverse_atan}


    def get_transformation(self, type):
        if type in self._transformation_dict:
            return self._transformation_dict[type]
        else:
            self.log.warning("Defaulting to linear transformation")
            return Map._transformation_linear

    def get_transformation_inverse(self, type):
        if type in self._transformation_inverse_dict:
            return self._transformation_inverse_dict[type]
        else:
            self.log.warning("Defaulting to linear transformation for inverse")
            return Map._transformation_linear


    def __init__(self, data, transformation="linear"):
        """
        test
        :param data:
        :param transformation:
        :return:
        """
        # TODO: alter cmap so that 0 is black and inf is white
        self.log = getModuleLogger(self)

        self._transformation = self.get_transformation(transformation)
        self._transformation_inverse = self.get_transformation_inverse(transformation)
        self.log.debug("Using transformation %s" % str(self._transformation))

        self._data = self._transformation(data)

        self._fig, self._ax = plt.subplots()
        self._canvas = FigureCanvas(self._fig)
        self._image = self._ax.imshow(self._data, origin="lower")
        self._image.set_interpolation('nearest')

        self._remove_axes()
        self._fig.set_facecolor('white')

        self._colorbar = None


    def use_region_outlines(self, new_value=True, region=None):
        # TODO: support this function
        if not isinstance(new_value, bool):
            raise TypeError("Expected the first argument to be a boolean")

        if not isinstance(region, Region):
            raise TypeError("Expected the second argument to be of type Region")

        self._use_region_outlines = True
        return

    def set_no_region_background(self, new_value=True, region=None):
        # TODO: support this function
        if not isinstance(new_value, bool):
            raise TypeError("Expected the first argument to be a boolean")

        if not isinstance(region, Region):
            raise TypeError("Expected the second argument to be of type Region")

        self._no_region_background = new_value

    def set_data_max_value(self, max_value=None):
        # TODO: write this function
        return

    def auto_clip_data(self, threshold=0.98):
        data_max = self._data.max()
        self.set_data_max_value(threshold * data_max)

    def save(self, filename=None):
        # TODO: write this function
        filename = filename or ( str(datetime.datetime.utcnow()) + ".png")
        self.log.debug("Saving to filename %s" % filename)
        self._canvas.print_png(filename)        # also accepts dpi= kwarg



    def _remove_axes(self):
        self._ax.get_xaxis().set_visible(False)
        self._ax.get_yaxis().set_visible(False)

    def remove_colorbar(self):
        self._fig.delaxes(self._fig.axes[1])


    def add_colorbar(self, vmin=None, vmax=None, label=None, decimal_precision=None):
        self._colorbar = self._fig.colorbar(self._image)

        # Values that exceed the colormap's values will be plotted as white. Those that
        # are below the minimum will be plotted as black.
        cmap = self._colorbar.cmap
        cmap.set_under('k')
        cmap.set_over('w')
        self._colorbar.set_cmap(cmap)

        if vmin is not None:
            vmin = self._transformation(vmin)
        else:
            vmin = 0
        if vmax is not None:
            vmax = self._transformation(vmax)
        else:
            vmax = numpy.max(self._data)*1.01
        self._image.set_clim(vmin, vmax)

        if decimal_precision is not None:
            self._label_num_decimals = decimal_precision

        if label is not None:
            self.set_colorbar_label(label)

        self._colorbar.ax.tick_params(labelsize=self.colorbar_font_size)

        max_caxis_transformed = vmax
        max_caxis = self._transformation_inverse(max_caxis_transformed)
        self.set_colorbar_ticks(max_caxis)




    # Assume that locations and labels are in *original* data coordinates
    def set_colorbar_ticks(self, locations, labels=None):
        # Generate list of locations if only one given
        # Note: need to transform to plot space first
        # In this mode, the input 'labels' is ignored
        if not isinstance(locations, list):
            max_transformed_location = self._transformation(locations)
            transformed_locations_temp = numpy.linspace(0, max_transformed_location, 11)
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
        (min_val, max_val) = self._colorbar.get_clim()
        tick_locations = numpy.linspace(min_val, max_val, num_ticks)
        self.set_colorbar_ticks(tick_locations)

    def blocking_show(self):
        plt.show()


    def set_colorbar_label(self, label):
        if self._colorbar is None:
            self.add_colorbar()
        self._colorbar.set_label(label, fontsize=self.colorbar_font_size, fontname=self.fontname)

        #print(dir(self._colorbar))

    def set_title(self, title):
        t = plt.title(title, fontsize=self.title_font_size, fontname=self.fontname)




# Source: http://stackoverflow.com/questions/4804005/matplotlib-figure-facecolor-background-color
# savefig('figname.png', facecolor=fig.get_facecolor(), transparent=True)




#
# data = numpy.random.random((200, 300)) * 100
# print "max from data = ", numpy.max(data)
# # make_map(data)
# new_map = Map(data)
# new_map.add_colorbar(decimal_precision=0)
# new_map.set_title("linear")
# # new_map.set_title("sample title")
# # #new_map.set_colorbar_ticks((0, .1, .5, .9, 1))
# # new_map.set_number_of_colorbar_ticks(4)
# # new_map.use_integer_labels(True)
# #new_map.save()
# #new_map.blocking_show()
# new_map.save("linear.png")
#
# # another_map = Map(data, transformation="log")
# # another_map.add_colorbar()
# # #another_map.set_colorbar_ticks((0, 20, 50, 100))
# # another_map.set_title("logarithmic")
# # another_map.save("log.png")
#
#
# #new_data = numpy.tril(numpy.round(numpy.random.random((200, 300)) * 4, 0) * 25)
# #new_data = numpy.matrix("[10 10 10; 30 30 30; 100 100 100]")
# new_data = numpy.matrix("[10 10 10; 30 30 30; 99 99 100]")
# third_map = Map(new_data, transformation="log")
# third_map.add_colorbar(vmax=110)
# third_map.set_title("log with discrete values")
# third_map.save("log2.png")
