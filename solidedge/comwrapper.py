import time
import logging
# noinspection PyUnresolvedReferences
from pywintypes import com_error

from config import lang

logger = logging.getLogger("LSF")

_DELAY = 0.05  # seconds
_TIMEOUT = 5.0  # seconds


def _com_call_wrapper(f, *args, **kwargs):
    """
    COMWrapper support function.
    Repeats calls when 'Call was rejected by callee.' exception occurs.
    """
    # Unwrap inputs
    args = [arg.wrapped_object if isinstance(arg, COMWrapper) else arg for arg in args]
    kwargs = {key: value.wrapped_object if isinstance(value, COMWrapper) else value for key, value in kwargs.items()}

    result = None
    start_time = time.time()
    while True:
        try:
            result = f(*args, **kwargs)
        except com_error as e:
            if e.hresult == -2147418111:
                print("Call was rejected by callee, retrying...")
                if time.time() - start_time >= _TIMEOUT:
                    raise
                time.sleep(_DELAY)
                continue
            elif e.hresult in (-2147417848, -2147352567):
                logger.warning(e)
            else:
                logger.warning(e)
                logger.error(lang.errors.com + str(e))
            raise
        break

    # if isinstance(result, (win32com.client.CDispatch, win32com.client.CoClassBaseClass)) or callable(result):
    if "win32com" in getattr(result, "__module__", "") or callable(result):
        return COMWrapper(result)
    return result


class COMWrapper:
    """
    Class to wrap COM objects to repeat calls when 'Call was rejected by callee.' exception occurs.
    """

    def __init__(self, wrapped_object):
        # assert isinstance(wrapped_object, win32com.client.CDispatch) or callable(wrapped_object)
        self.__dict__['wrapped_object'] = wrapped_object

    def __getattr__(self, item):
        # return _com_call_wrapper(self.wrapped_object.__getattr__, item)
        return _com_call_wrapper(getattr, self, item)

    def __getitem__(self, item):
        return _com_call_wrapper(self.wrapped_object.__getitem__, item)

    def __setattr__(self, key, value):
        # _com_call_wrapper(self.wrapped_object.__setattr__, key, value)
        _com_call_wrapper(setattr, self, key, value)

    def __setitem__(self, key, value):
        _com_call_wrapper(self.wrapped_object.__setitem__, key, value)

    def __call__(self, *args, **kwargs):
        return _com_call_wrapper(self.wrapped_object.__call__, *args, **kwargs)

    def __repr__(self):
        return 'ComWrapper<{}>'.format(repr(self.wrapped_object))

    def __eq__(self, other):
        if isinstance(other, COMWrapper):
            return self.wrapped_object == other.wrapped_object
        return False
