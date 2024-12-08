#todo: out of date

import os
from pathlib import Path
from typing import TypedDict, Optional, List
from ..app.git import git_update_repo
from . import get_app_config_path   
from zuu.std.json import read_json, touch_json, write_json
from zuu.util.singleton import absoluteSingleton
import time

path = get_app_config_path("gitcacher")


class GitCacher(metaclass=absoluteSingleton()):
    class _CacheUnit(TypedDict):
        last: int
        interval: int
        giturl: str
        name: str
        usr: str
        branch: str

    def __init__(self):
        self.__configPath = os.path.join(path, "config.json")
        touch_json(self.__configPath, default="[]")
        self.__config: List[self._CacheUnit] = read_json(self.__configPath)
        self.__cachePath = os.path.join(path, "cache")
        os.makedirs(self.__cachePath, exist_ok=True)
        self.check_expired()

    def add(self, giturl: str, branch: str = None, setExpire: int = 24 * 60 * 60):
        """
        Add a new git repository to the cache.

        :param giturl: URL of the git repository.
        :param branch: Branch to checkout.
        :param setExpire: Expiration time in seconds.
        """
        gitname = giturl.split("/")[-1].split(".")[0]
        gitusr = giturl.split("/")[-2]

        if any(
            entry["name"] == gitname
            and entry["usr"] == gitusr
            and entry["branch"] == branch
            for entry in self.__config
        ):
            self.check_expired(gitname, gitusr)
            return

        git_update_repo(
            os.path.join(self.__cachePath, f"{gitusr}_{gitname}"), giturl, branch
        )

        self.__config.append(
            {
                "last": int(time.time()),
                "interval": setExpire,
                "giturl": giturl,
                "name": gitname,
                "usr": gitusr,
                "branch": branch,
            }
        )
        write_json(self.__configPath, self.__config)

    def get(
        self,
        path: str,
        usr: Optional[str] = None,
        name: Optional[str] = None,
        branch: Optional[str] = None,
        fuzzyMatch: bool = False,
    ):
        """
        Get a file from the cache.

        :param usr: User of the repository.
        :param name: Name of the repository.
        :param path: Path to the file.
        :return: Path to the file in the cache.
        """
        for entry in self.__config:
            usr_match = usr is None or entry["usr"] == usr
            name_match = name is None or entry["name"] == name
            branch_match = branch is None or entry["branch"] == branch
            if not (usr_match and name_match and branch_match):
                continue
            opath = os.path.join(self.__cachePath, f"{entry['usr']}_{entry['name']}")
            cpath = os.path.join(opath, Path(path))
            if os.path.exists(cpath):
                return cpath

            if not fuzzyMatch:
                continue

            for root, dirs, files in os.walk(opath):
                for file in files:
                    if os.path.join(root, file).endswith(path):
                        return os.path.join(root, file)

        return None

    def check_expired(self, name: str = None, usr: str = None, branch: str = None):
        """
        Check for expired cache entries and update them if necessary.
        """
        current_time = int(time.time())
        for entry in self.__config:

            if name and entry["name"] != name:
                continue

            if usr and entry["usr"] != usr:
                continue

            if branch and entry["branch"] != branch:
                continue

            entrypath = os.path.join(
                self.__cachePath, f"{entry['usr']}_{entry['name']}"
            )

            if current_time - entry["last"] > entry["interval"]:
                git_update_repo(entrypath, entry["giturl"])
                entry["last"] = current_time
        write_json(self.__configPath, self.__config)


    def singleStringQuery(
        self,
        string : str
    ):
        if ":" not in string:
            return self.get(
                string, fuzzyMatch=True
            )
        
        splitted = string.split(":")
        queryPart = splitted[0].split("/")
        stringPart = splitted[1]

        if len(queryPart) == 2:
            return self.get(
                stringPart,
                usr=queryPart[0],
                name=queryPart[1],
                fuzzyMatch=True
            )
            
        queryDict = {}
        for part in queryPart:
            if "=" not in part:
                raise ValueError("Invalid query")
            
            queryDict[part.split("=")[0]] = part.split("=")[1]

        return self.get(
            stringPart,
            **queryDict,
            fuzzyMatch=True
        )
    
GLOBAL_CACHER = GitCacher()

def resolve_path(path : str):
    if not path.startswith("@") and os.path.exists(path):
        return path
    path = path.removeprefix("@")
    return GLOBAL_CACHER.singleStringQuery(path)