import typing
import pygetwindow as gw

def activate_wnd(wnd: gw.BaseWindow):
    """
    Activates the given window if it is not already active.

    Args:
        wnd (gw.Window): The window to activate.

    Returns:
        None

    Raises:
        None
    """
    try:
        if wnd.isActive:
            return
        wnd.activate()
    except gw.PyGetWindowException:
        pass


def get_window_pos(wnd: gw.BaseWindow) -> typing.Tuple[float, float, float, float]:
    """
    Get the position and size of the window.

    Args:
        wnd (gw.Window): The window from which to retrieve the position and size.

    Returns:
        typing.Tuple[float, float, float, float]: A tuple containing the left, top, width, and height of the window.
    """
    return (wnd.left, wnd.top, wnd.width, wnd.height)


def filter_visible_windows(
    wnds: typing.Iterable[gw.BaseWindow],
) -> typing.List[gw.BaseWindow]:
    rwnds = []
    for wnd in wnds:
        if wnd.height > 0 and wnd.width > 0:
            rwnds.append(wnd)
    return rwnds


def filter_titled_windows(
    wnds: typing.Iterable[gw.BaseWindow],
) -> typing.List[gw.BaseWindow]:
    """
    Filter non-titled windows.

    Args:
        wnds (typing.Iterable[gw.Window]): An iterable of windows to filter.

    Returns:
        typing.List[gw.Window]: A list of windows with titles.
    """
    rwnds = []
    for wnd in wnds:
        if wnd.title:
            rwnds.append(wnd)
    return rwnds


class WindowGather:
    """
    A context manager that tracks window changes during its lifetime.

    This class monitors windows that are added, removed, or remain unchanged while
    the context is active. By default, it filters out invisible and untitled windows.

    Args:
        filterVisible (bool, optional): Whether to filter out invisible windows. Defaults to True.
        filterTitled (bool, optional): Whether to filter out untitled windows. Defaults to True.

    Example:
        >>> with WindowGather() as wg:
        ...     # Do something that may create or close windows
        ...     pass
        >>> added_windows = wg.added  # List of new windows
        >>> removed_windows = wg.removed  # List of closed windows
        >>> unchanged_windows = wg.unchanged  # List of windows that stayed open

    Properties:
        added: List of new windows created during the context
        removed: List of windows closed during the context
        unchanged: List of windows that remained open throughout
    """
    def __init__(self, filterVisible: bool = True, filterTitled: bool = True):
        self.__changedWindows : dict = {}
        self.__filterVisible = filterVisible
        self.__filterTitled = filterTitled

    def _gather(self):
        wnds : typing.Dict[int |str, gw.BaseWindow] = gw.getAllWindows()
        if self.__filterVisible:
            wnds = filter_visible_windows(wnds)
        if self.__filterTitled:
            wnds = filter_titled_windows(wnds)

        try:
            from pygetwindow import Win32Window
            wnds = {wnd._hWnd: wnd for wnd in wnds}
        except Exception:
            wnds = {wnd.title(): wnd for wnd in wnds}
        return wnds
    

    @property
    def added(self):
        return list(self.__changedWindows.get("added", []))
    
    @property
    def removed(self):
        return list(self.__changedWindows.get("removed", []))
    
    @property
    def unchanged(self):
        return list(self.__changedWindows.get("unchanged", []))

    def __enter__(self):
        self.__windows = self._gather()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        newwnds = self._gather()
        changes = {
            "added" : [],
            "removed" : [],
            "unchanged" : []
        }
        for id, wnd in self.__windows.items():
            if id not in newwnds:
                changes["removed"].append(wnd)
            else:
                changes["unchanged"].append(wnd)
        for id, wnd in newwnds.items():
            if id not in self.__windows:
                changes["added"].append(wnd)

        self.__changedWindows = changes


