
class Device(object):
    """This class describes a whitespace device."""

    def __init__(self, is_portable, haat_meters=None, has_geolocation=None):
        self._is_portable = is_portable
        self._haat_meters = haat_meters
        self._has_geolocation = has_geolocation

    def is_portable(self):
        """Returns True if the device is personal/portable and False otherwise."""
        return self._is_portable

    def has_geolocation(self):
        """Returns True if the device has geolocation capabilities and False otherwise. May return None."""
        return self._has_geolocation

    def get_haat(self):
        """Returns the HAAT of the device in meters. May return None."""
        return self._haat_meters
