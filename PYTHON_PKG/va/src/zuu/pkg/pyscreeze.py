
import logging as _logging
import pyscreeze

__all__ = [
    "center",
    "locateAll",
    "locateAllOnScreen",
    "locateCenterOnScreen",
    "locateOnScreen",
    "locateOnWindow",
    "pixel",
    "pixelMatchesColor",
    "screenshot",
    #
    "screenshot_win32_full",
    "overload_screenshot_win32_to_all",
    "boxcenter"
]

from pyscreeze import (  # noqa: E402
    center as center,
    locateAll as locateAll,
    locateAllOnScreen as locateAllOnScreen,
    locateCenterOnScreen as locateCenterOnScreen,
    locateOnScreen as locateOnScreen,
    locateOnWindow as locateOnWindow,
    pixel as pixel,
    pixelMatchesColor as pixelMatchesColor,
    screenshot as screenshot
)

def screenshot_win32_full(imageFilename=None, region=None, allScreens=True):
    from pyscreeze import _screenshot_win32

    return _screenshot_win32(imageFilename, region, allScreens)

def overload_screenshot_win32_to_all():
    from pyscreeze import _screenshot_win32
    

    def _screenshot_win32_full(imageFilename=None, region=None, allScreens=True):
        return _screenshot_win32(imageFilename, region, allScreens)

    pyscreeze._screenshot_win32 = _screenshot_win32_full
    _logging.info("overwritten pyscreeze._screenshot_win32")


def boxcenter(box):
    """
    Calculate the center coordinates of the given box.

    Parameters:
        box : tuple or Box
            The input box for which to calculate the center coordinates.

    Returns:
        Point
            The center coordinates of the box as a Point object.
    """
    if isinstance(box, tuple):
        return pyscreeze.center(box)
    return pyscreeze.Point(box.left + box.width / 2, box.top + box.height / 2)