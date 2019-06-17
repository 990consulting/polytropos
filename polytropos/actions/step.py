from abc import abstractmethod
from collections.abc import Callable

class Step(Callable):

    @abstractmethod
    def __call__(self, origin_dir: str, target_dir: str):
        """Call takes the origin folder and the target folder
        :param origin_dir: The directory path in which to find origin composites
        :param target_dir: The directory path in which to find target composites
        """
        pass
