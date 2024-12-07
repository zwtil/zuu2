import functools
import logging
from zuu.pkg.psutil import ProcessGather
from zuu.pkg.pygetwindow import WindowGather
import psutil

def timelyKill(
    process_monitor : bool = True, 
    window_monitor : bool = True, 
    monitor_objs : list = [],
    kill : bool = True,
    logger : logging.Logger = logging.getLogger(__name__)
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if process_monitor:
                monitor_objs.append(ProcessGather())
            if window_monitor:
                monitor_objs.append(WindowGather()) 
            for obj in monitor_objs:
                obj.__enter__()
            try:
                res = func(*args, **kwargs)
            finally:
                for obj in monitor_objs:
                    obj.__exit__(None, None, None)

            func.__monitors__ = monitor_objs

            if kill:
                for monitor in monitor_objs:
                    if isinstance(monitor, WindowGather):
                        for wnd in monitor.added:
                            try:
                                wnd.close()
                            except Exception as e:
                                logger.error(e)
                    elif isinstance(monitor, ProcessGather):
                        for proc in monitor.added:
                            try:
                                logger.info(f"killing {proc.pid} {proc.name()}")
                                proc.kill()
                            except psutil.NoSuchProcess:
                                logger.error(f"NoSuchProcess {proc.pid} {proc.name()}")

            return res
        return wrapper
    return decorator
