from typing import NoReturn

import tblib.pickling_support
import sys

tblib.pickling_support.install()

class ExceptionWrapper(object):

    def __init__(self, ee: BaseException):
        self.ee = ee
        _type,  _value, self.tb = sys.exc_info()

    def re_raise(self) -> NoReturn:
        raise self.ee.with_traceback(self.tb)
