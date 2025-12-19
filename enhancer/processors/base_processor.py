from abc import ABC, abstractmethod

class ImageProcessor(ABC):
    """
    Abstract base class for image processing algorithms.
    """
    @property
    @abstractmethod
    def name(self):
        """
        Returns the name of the algorithm.
        """
        pass

    @abstractmethod
    def get_parameters(self):
        """
        Returns a dictionary of parameters for the algorithm.
        """
        pass

    @abstractmethod
    def process(self, image, params):
        """
        Processes the image using the algorithm.
        """
        pass
