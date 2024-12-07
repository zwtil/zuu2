import psutil

def iter_user_processes():
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            if not proc.info['username']:
                continue

            if proc.info['username'].endswith('SERVICE') or 'SYSTEM' in proc.info['username']:
                continue

            yield proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def iter_system_processes():
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            if not proc.info['username']:
                continue

            if proc.info['username'].endswith('SERVICE') or 'SYSTEM' in proc.info['username']:
                yield proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

class ProcessGather:
    """
    A context manager that tracks process changes during its lifetime.

    This class monitors processes that are added, removed, or remain unchanged while
    the context is active. By default, it only tracks user processes and ignores
    system processes.

    Args:
        ignoreSystem (bool, optional): Whether to ignore system processes. Defaults to True.

    Example:
        >>> with ProcessGather() as pg:
        ...     # Do something that may create or terminate processes
        ...     pass
        >>> added_processes = pg.added  # List of new processes
        >>> removed_processes = pg.removed  # List of terminated processes
        >>> unchanged_processes = pg.unchanged  # List of processes that stayed active

    Properties:
        added: List of new processes created during the context
        removed: List of processes terminated during the context
        unchanged: List of processes that remained active throughout
    """
    def __init__(self, ignoreSystem : bool = True):
        self.__changedProcesses = {}
        self.__ignoreSystem = ignoreSystem

    def _gather(self):
        return {proc.pid : proc for proc in iter_user_processes()}
    def __enter__(self):
        self.__processes = self._gather()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        procs = self._gather()
        added =  procs.keys() - self.__processes.keys()
        removed = self.__processes.keys() - procs.keys()
        unchanged = self.__processes.keys() & procs.keys()
        def get_root_process(processes, pid, proc_dict):
            try:
                proc = proc_dict[pid]
            except (KeyError, psutil.NoSuchProcess):
                return None
            parent = proc.parent()
            if parent is None or parent.pid not in processes:
                return proc
            return get_root_process(processes, parent.pid, proc_dict)

        self.__changedProcesses = {
            "added": set(get_root_process(added, pid, procs) for pid in added),
            "removed": set(get_root_process(removed, pid, self.__processes) for pid in removed), 
            "unchanged": set(self.__processes[pid] for pid in unchanged)
        }

        # filter out none values
        self.__changedProcesses["added"] = {proc.pid : proc for proc in self.__changedProcesses["added"] if proc is not None}
        self.__changedProcesses["removed"] = {proc.pid : proc for proc in self.__changedProcesses["removed"] if proc is not None}
        self.__changedProcesses["unchanged"] = {proc.pid : proc for proc in self.__changedProcesses["unchanged"] if proc is not None}

    @property
    def added(self):
        return list(self.__changedProcesses.get("added", {}).values())
    
    @property
    def removed(self):
        return list(self.__changedProcesses.get("removed", {}).values())
    
    @property
    def unchanged(self):
        return list(self.__changedProcesses.get("unchanged", {}).values())

