from propagation_model import PropagationModel
# from doc_inherit import doc_inherit
from math import log


class PropagationModelFreeSpace(PropagationModel):
    """This class implements the free-space propagation model. For more details,
    see http://en.wikipedia.org/wiki/Free-space_path_loss"""


    def __init__(self, *args, **kwargs):
        super(PropagationModelFreeSpace, self).__init__(*args, **kwargs)

        self.log.warning("Not the actual FSPL model!")


    # These define the external parameters of the model
    # @doc_inherit
    def requires_terrain(self):
        return False

    # @doc_inherit
    def requires_tx_height(self):
        return False

    # @doc_inherit
    def requires_rx_height(self):
        return False

    # @doc_inherit
    def requires_frequency(self):
        return False

    def requires_tx_location(self):
        return True

    def requires_rx_location(self):
        return True

    def requires_curve_enum(self):
        return False

    exponent = 2

    # TODO: Update to use the actual FSPL model
    def get_pathloss_coefficient_unchecked(self, distance, frequency=None, tx_height=None, rx_height=None,
                                           tx_location=None, rx_location=None, curve_enum=None):
        return (1/(float(distance) ** self.exponent))



    def get_distance_unchecked(self, pathloss_coefficient, frequency=None, tx_height=None, rx_height=None,
                               tx_location=None, rx_location=None,
                     curve_enum=None):
        if pathloss_coefficient is None:
            return None

        return log(pathloss_coefficient, self.exponent)
