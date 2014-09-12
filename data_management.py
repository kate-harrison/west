from abc import ABCMeta, abstractmethod, abstractproperty
from ruleset import Ruleset
from device import Device
from propagation_model import PropagationModel
from region import Region
from boundary import Boundary
from data_map import DataMap2D, DataMap3D
from population import PopulationData
from custom_logging import getModuleLogger
import os
import textwrap

base_data_directory = "data"


def _is_class(obj):
    """Returns True if ``obj`` is a class and False if it is an instance."""
    return issubclass(obj.__class__, type)


def _is_object(obj):
    """Returns True if ``obj`` is an instance and False if it is a class."""
    return not _is_class(obj)


def _make_string(obj):
    def obj_belongs_to(class_object):
        return (_is_class(obj) and issubclass(obj, class_object)) or (_is_object(obj) and isinstance(obj, class_object))

    def get_class_name():
        if _is_class(obj):
            return obj.__name__
        else:
            return obj.__class__.__name__

    if obj_belongs_to(Ruleset) or obj_belongs_to(PropagationModel) or obj_belongs_to(Boundary) or obj_belongs_to(DataMap2D):
        return get_class_name()
    elif obj_belongs_to(Device):
        if _is_class(obj):
            raise TypeError("Expected an actual Device object.")
        else:
            if obj.is_portable():
                return "Device(portable)"
            else:
                return "Device(fixed,HAAT=%d)" % obj.get_haat()
    elif obj_belongs_to(Region):
        return get_class_name()


class Specification(object):
    """
    A Specification is the minimum amount of information needed to describe a set of data. A Specification can be used
    to create data, fetch data, and automatically map data.

    Specifications are best-effort data caches which are meant to aid in data generation and organization.

    Guiding principles:

       * The user is responsible for cache invalidation.
       * A best-effort attempt at avoiding naming collisions has been made but nothing should be considered certain.
       * When possible, load data from disk. When not possible, generate the data, save it, and then load it from disk.
       * When possible, allow the user to specify either a class name or an instance of the class. If an instance is
         specified, that instance will be used if an instance is needed. Otherwise, an instance will be created only
         when it becomes necessary for data generation.

    Notes for extending this class:

       * Become familiar with the use of the many helper functions. See e.g. the init function for
         :class:`SpecificationWhitespaceMap` for example usage.
       * Be sure that :meth:`make_data` returns the data in addition to saving it.
       * Implement :meth:`get_map` if possible.
       * Filenames should not exceed 255 characters in order to be compatible with common file systems.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_string(self):
        """Returns the string representation of the Specification."""
        pass

    @abstractproperty
    def subdirectory(self):
        """Returns a string with the name of the data subdirectory to be used for storing the data created by this
        Specification."""
        pass

    @abstractmethod
    def make_data(self):
        """
        Creates the data based on the information in the Specification. Must both save and return created data.

        See also: :meth:`save_data`.
        """
        pass

    def get_map(self):
        """Optionally-implemented method which will create the default map for the Specification."""
        raise NotImplementedError("")

    def _get_datamap_spec(self):
        """If possible, returns the internal :class:`SpecificationDataMap`. To succeed, the Specification must satisfy
        at least one of the following:

           * Be a SpecificationDataMap
           * Have an attribute "datamap_spec" which is a SpecificationDataMap object
           * Have an attribute "region_map_spec" which is a SpecificationRegionMap object

        Raises an AttributeError if no SpecificationDataMap is found.
        """
        if isinstance(self, SpecificationDataMap):
            return self
        if hasattr(self, "datamap_spec"):
            return self.datamap_spec
        if hasattr(self, "region_map_spec"):
            return self.region_map_spec._get_datamap_spec()

        raise AttributeError("No datamap specification found (expected to find one of the following attributes: "
                             "datamap_spec, region_map_spec")

    def _convert_to_class_and_object(self, var_name, obj, may_create_new_objects=True, **kwargs):
        """
        Sets the internal variables [var_name]_class, [var_name]_object based on ``obj``. ``obj`` may be either a class
        or an instance of a class.

        If ``obj`` is a class, the object will be created only if ``may_create_new_objects`` is True. In that case, the
        keyword arguments are passed to the constructor.

        If ``obj`` is an instance, that instance will be used.
        """
        if _is_class(obj):
            setattr(self, var_name + "_class", obj)
            if may_create_new_objects:
                setattr(self, var_name + "_object", obj(**kwargs))
        else:
            setattr(self, var_name + "_object", obj)
            setattr(self, var_name + "_class", obj.__class__)

    def _boundary_to_class_and_object(self, boundary):
        self._convert_to_class_and_object("boundary", boundary)

    def _region_to_class_and_object(self, region):
        self._convert_to_class_and_object("region", region)

    def _ruleset_to_class_and_object(self, ruleset):
        self._convert_to_class_and_object("ruleset", ruleset)

    def _propagation_model_to_class_and_object(self, propagation_model):
        self._convert_to_class_and_object("propagation_model", propagation_model)

    def _store_at_least_class(self, var_name, obj):
        """Stores at minimum the class of ``obj``. If ``obj`` is an instance (rather than a class), ``obj`` will be
        stored as well."""
        self._convert_to_class_and_object(var_name, obj, may_create_new_objects=False)

    def _create_obj_if_needed(self, var_name, **kwargs):
        """If [var_name]_object does not exist, create it. In that case, the keyword arguments are passed to the
        constructor."""
        if hasattr(self, var_name + "_object"):
            return

        obj_class = getattr(self, var_name + "_class")
        setattr(self, var_name + "_object", obj_class(**kwargs))

    def _expect_of_type(self, obj, expected_types):
        """Raise a TypeError if ``obj`` is neither a subclass nor an instance of one of the expected types.
        expected_types may be either a list or a singleton."""
        if not isinstance(expected_types, list):
            expected_types = [expected_types]

        for e_type in expected_types:
            if not _is_class(e_type):
                raise TypeError("Expected type must be a class (got '%s' instead)." % str(expected_types))

        if _is_class(obj):
            cls = obj
        else:
            cls = obj.__class__

        is_wrong_type = True
        for e_type in expected_types:
            if issubclass(cls, e_type):
                is_wrong_type = False

        if is_wrong_type:
            raise TypeError("Expected something of a type in %s (either a class or object) but received something of "
                            "type %s." % (str(expected_types), cls.__name__))

    def _expect_is_object(self, obj):
        """Raise a TypeError if ``obj`` is not an instance."""
        if not _is_object(obj):
            raise TypeError("Expected to receive an instance and instead received %s." % str(obj))

    def _expect_is_class(self, obj):
        """Raise a TypeError if ``obj`` is not a class."""
        if not _is_class(obj):
            raise TypeError("Expected to receive a class and instead received %s." % str(obj))

    @property
    def filename(self):
        """Returns a string which is the full path to the file."""
        return os.path.join(self.full_directory, self.to_string() + ".pkl")

    @property
    def full_directory(self):
        """Returns a string which is the full directory path in which the file will be stored."""
        return os.path.join(base_data_directory, self.subdirectory)

    def data_exists(self):
        """Returns True if data with the associated filename already exists and False otherwise."""
        return os.path.isfile(self.filename)

    def load_data(self):
        """Loads the :class:`data_map.DataMap2D` or :class:`data_map.DataMap3D` from a pickle. The filename is
        determined by :meth:`filename`."""
        if self._get_datamap_spec().is_datamap2d():
            return DataMap2D.from_pickle(self.filename)
        else:
            return DataMap3D.from_pickle(self.filename)

    def save_data(self, datamap):
        """Save the :class:`data_map.DataMap2D` or :class:`data_map.DataMap3D` to a pickle. The filename is determined
        by :meth:`filename`."""
        self._expect_of_type(datamap, [DataMap2D, DataMap3D])
        if not os.path.isdir(self.full_directory):
            os.makedirs(self.full_directory)
        datamap.to_pickle(self.filename)

    def fetch_data(self):
        """Fetch the data described by this Specification. If none exists, the data will be made and then loaded.

        Components: :meth:`load_data`, :meth:`make_data`
        """
        if not hasattr(self, "log"):
            self.log = getModuleLogger(self)
        if self.data_exists():
            self.log.debug("Fetching data (LOAD): %s" % self.to_string())
            data = self.load_data()
        else:
            self.log.debug("Fetching data (MAKE): %s" % self.to_string())
            data = self.make_data()
        if data is None:
            raise ValueError("No data loaded")
        return data

    def _set_map_title(self, map):
        """Automatically sets the map title from the filename."""
        map.title_font_size = 10
        wrapped_title = "\n".join(textwrap.wrap(self.to_string(), 80))
        map.set_title(wrapped_title)


class SpecificationDataMap(Specification):
    """
    This Specification describes a :class:`data_map.DataMap2D` or :class:`data_map.DataMap3D`. The Specification must
    be created with a derived class, e.g. :class:`data_map.DataMap2DContinentalUnitedStates`.

    Unlike other classes, it will *always* create a new DataMap2D/DataMap3D when "making" or fetching data. Data will
    never be saved.
    """
    def __init__(self, datamap_derived_class, num_latitude_divisions, num_longitude_divisions):
        self._expect_of_type(datamap_derived_class, [DataMap2D, DataMap3D])
        self._expect_of_type(num_latitude_divisions, int)
        self._expect_of_type(num_longitude_divisions, int)

        if datamap_derived_class is DataMap2D or datamap_derived_class is DataMap3D:
            raise TypeError("The DataMap2D class must be a derived class which specified the latitude and longitude "
                            "bounds of the data map.")

        self._store_at_least_class("datamap", datamap_derived_class)
        self.num_latitude_divisions = num_latitude_divisions
        self.num_longitude_divisions = num_longitude_divisions

    def to_string(self):
        return "%s_%dx%d" % (_make_string(self.datamap_class), self.num_latitude_divisions,
                             self.num_longitude_divisions)

    def make_data(self):
        return self.datamap_class.create(self.num_latitude_divisions, self.num_longitude_divisions)

    @property
    def subdirectory(self):
        # Data is never saved
        return None

    def is_datamap2d(self):
        """Returns True if this Specification describes a :class:`data_map.DataMap2D`."""
        return issubclass(self.datamap_class, DataMap2D)

    def is_datamap3d(self):
        """Returns True if this Specification describes a :class:`data_map.DataMap3D`."""
        return issubclass(self.datamap_class, DataMap3D)

    def data_exists(self):
        # Override the natural behavior so that the Specification never tried to load the data
        return False


class SpecificationRegionMap(Specification):
    """
    This Specification describes a :class:`data_map.DataMap2D` which contains boolean data. Values will be True (or
    truthy) if and only if the pixel's center is inside the :class:`boundary.Boundary`.
    """
    def __init__(self, boundary, datamap_spec):
        self._expect_of_type(boundary, Boundary)
        self._expect_of_type(datamap_spec, SpecificationDataMap)
        if not datamap_spec.is_datamap2d():
            raise TypeError("The datamap spec must describe a DataMap2D.")

        self._store_at_least_class("boundary", boundary)
        self.datamap_spec = datamap_spec

    def make_data(self):
        self._create_obj_if_needed("boundary")
        boundary = self.boundary_object

        datamap = self.datamap_spec.fetch_data()

        def is_in_region(latitude, longitude, latitude_index, longitude_index, current_value):
            location = (latitude, longitude)
            return boundary.location_inside_boundary(location)

        datamap.update_all_values_via_function(update_function=is_in_region)
        self.save_data(datamap)

        return datamap

    def to_string(self):
        return " ".join(["REGION_MAP", _make_string(self.boundary_class), self.datamap_spec.to_string()])

    @property
    def subdirectory(self):
        return "REGION_MAP"

    def get_map(self):
        """Creates a linear-scale :class:`map.Map` with boundary outlines and a white background. The title is
        automatically set using the Specification information but can be reset with :meth:`map.Map.set_title`.
        Returns a handle to the map object; does not save or show the map."""
        datamap = self.fetch_data()
        self._create_obj_if_needed("boundary")
        map = datamap.make_map(is_in_region_map=datamap)
        map.add_boundary_outlines(self.boundary_object)
        self._set_map_title(map)
        return map

class SpecificationWhitespaceMap(Specification):
    """
    This Specification describes a :class:`data_map.DataMap3D` which is True (or truthy) for pixels which are considered
    whitespace for the device in accordance with the :class:`ruleset.Ruleset`.

    The resulting DataMap3D has layers described by :meth:`region.Region.get_tvws_channel_list()`.

    .. note:: The naming conventions for this class assume that the default \
        :class:`protected_entities.ProtectedEntities` for the :class:`region.Region` should be used. To specify \
        alternative protected entities, create a new class derived from the desired Region.
    """
    def __init__(self, region_map_spec, region, ruleset, device_object, propagation_model=None):

        # Type checking
        self._expect_of_type(region_map_spec, SpecificationRegionMap)
        self._expect_of_type(region, Region)
        self._expect_of_type(ruleset, Ruleset)
        self._expect_is_object(device_object)

        # Store data
        self.region_map_spec = region_map_spec
        self._store_at_least_class("region", region)
        self._store_at_least_class("ruleset", ruleset)
        self._convert_to_class_and_object("device", device_object)

        # Propagation model needs special handling
        if propagation_model is None:
            self._create_obj_if_needed("ruleset")
            propagation_model = self.ruleset_object.get_default_propagation_model()
        self._expect_of_type(propagation_model, PropagationModel)
        self._store_at_least_class("propagation_model", propagation_model)


    def to_string(self):
        return " ".join(["WHITESPACE_MAP", "(%s)" % self.region_map_spec.to_string(),
                         _make_string(self.region_class),
                         _make_string(self.ruleset_class), _make_string(self.propagation_model_class),
                         _make_string(self.device_object)])

    @property
    def subdirectory(self):
        return "WHITESPACE_MAP"

    def make_data(self):
        self._create_obj_if_needed("region")
        self._create_obj_if_needed("propagation_model")
        self.ruleset_object.set_propagation_model(self.propagation_model_object)

        region_datamap = self.region_map_spec.fetch_data()

        channel_list = self.region_object.get_tvws_channel_list()
        whitespace_datamap3d = DataMap3D.from_DataMap2D(region_datamap, channel_list)
        for channel in channel_list:
            channel_layer = whitespace_datamap3d.get_layer(channel)
            self.ruleset_object.turn_datamap_into_whitespace_map(self.region_object, channel_layer, channel,
                                                                 self.device_object)

        self.save_data(whitespace_datamap3d)
        return whitespace_datamap3d

    def get_map(self):
        """Creates a linear-scale :class:`map.Map` with boundary outlines, a white background, and a colorbar. The title
        is automatically set using the Specification information but can be reset with :meth:`map.Map.set_title`.
        Returns a handle to the map object; does not save or show the map."""
        datamap3d = self.fetch_data()
        datamap2d = datamap3d.sum_all_layers()

        region_map = self.region_map_spec.fetch_data()
        self.region_map_spec._create_obj_if_needed("boundary")
        boundary = self.region_map_spec.boundary_object

        map = datamap2d.make_map(is_in_region_map=region_map)
        map.add_boundary_outlines(boundary)
        map.add_colorbar(decimal_precision=0)
        map.set_colorbar_label("Number of available whitespace channels")
        self._set_map_title(map)
        return map


class SpecificationRegionAreaMap(Specification):
    """
    This Specification describes a :class:`data_map.DataMap2D` where the value of each pixel describes the area (in
    square kilometers) of the pixel.

    This data may be useful e.g. to create a CDF by area using :meth:`data_manipulation.calculate_cdf_from_datamap2d`.
    """
    def __init__(self, datamap_spec):
        self._expect_of_type(datamap_spec, SpecificationDataMap)
        self._expect_is_object(datamap_spec)
        self.datamap_spec = datamap_spec

    @property
    def subdirectory(self):
        return "REGION_AREA"

    def to_string(self):
        return " ".join(["REGION_AREA", "(%s)" % self.datamap_spec.to_string()])

    def make_data(self):
        from geopy.distance import vincenty

        datamap = self.datamap_spec.fetch_data()

        latitude_width = float(datamap.latitudes[1] - datamap.latitudes[0])
        longitude_width = float(datamap.longitudes[1] - datamap.longitudes[0])

        def create_pixel_area(latitude, longitude, latitude_index, longitude_index, current_value):
            # Calculate its area by pinpointing each corner of the trapezoid it represents
            # Assume that it extends lat_div_size/2 east-west
            NW_lat = latitude + latitude_width/2
            SW_lat = NW_lat
            NE_lat = latitude - latitude_width/2
            SE_lat = NE_lat

            # Assume that it extends long_div_size/2 north-south
            NW_lon = longitude + longitude_width/2
            SW_lon = longitude - longitude_width/2
            NE_lon = NW_lon
            SE_lon = SW_lon

            height = vincenty((NW_lat, NW_lon), (SW_lat, SW_lon)).kilometers
            top = vincenty((NW_lat, NW_lon), (NE_lat, NE_lon)).kilometers
            bottom = vincenty((SW_lat, SW_lon), (SE_lat, SE_lon)).kilometers

            return 0.5*height*(top+bottom)

        datamap.update_all_values_via_function(update_function=create_pixel_area)
        self.save_data(datamap)
        return datamap

    def get_map(self):
        """Creates a linear-scale :class:`map.Map` with a colorbar. The title is automatically set using the
        Specification information but can be reset with :meth:`map.Map.set_title`. Returns a handle to the map object;
        does not save or show the map."""
        datamap = self.fetch_data()
        map = datamap.make_map()
        map.add_colorbar()
        map.set_colorbar_label("Area of pixel (km^2)")
        self._set_map_title(map)
        return map


class SpecificationPopulationMap(Specification):
    """
    This Specification describes a :class:`data_map.DataMap2D` where the value of each pixel is the population of the
    pixel (in people).

    This data may be useful e.g. to create a CDF by population using
    :meth:`data_manipulation.calculate_cdf_from_datamap2d`.


    """
    def __init__(self, region_map_spec, population):
        self._expect_of_type(region_map_spec, SpecificationRegionMap)
        self._expect_of_type(population, PopulationData)

        self.region_map_spec = region_map_spec
        self._store_at_least_class("population", population)

    @property
    def subdirectory(self):
        return "POPULATION"

    def to_string(self):
        return " ".join(["POPULATION", "(%s)" % self.region_map_spec.to_string()])

    def make_data(self):
        self._create_obj_if_needed("population")
        region_datamap = self.region_map_spec.fetch_data()
        population_datamap = self.population_object.create_population_map(is_in_region_datamap2d=region_datamap)
        self.save_data(population_datamap)
        return population_datamap

    def get_map(self):
        """Creates a log-scale :class:`map.Map` with boundary outlines, a white background, and a colorbar. The title
        is automatically set using the Specification information but can be reset with :meth:`map.Map.set_title`.
        Returns a handle to the map object; does not save or show the map."""
        datamap = self.fetch_data()
        region_datamap = self.region_map_spec.fetch_data()
        self.region_map_spec._create_obj_if_needed("boundary")
        boundary = self.region_map_spec.boundary_object

        map = datamap.make_map(transformation='log', is_in_region_map=region_datamap)
        map.add_colorbar()
        map.set_colorbar_label("Population")
        map.add_boundary_outlines(boundary)
        self._set_map_title(map)
        return map
