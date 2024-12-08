import os
import time
import json
import typing

def new_ver4_library(path: str, make_dirs: bool = True):
    if make_dirs:
        os.makedirs(path, exist_ok=True)
    
    assert os.path.isdir(path)

    os.makedirs(os.path.join(path, "backup"), exist_ok=True)
    os.makedirs(os.path.join(path, "images"), exist_ok=True)

    if not os.path.exists(os.path.join(path, "tags.json")):
        with open(os.path.join(path, "tags.json"), "w") as f:
            f.write('\{"historyTags : [], "starredTags": []\}')

    if not os.path.exists(os.path.join(path, "saved-filters.json")):
        with open(os.path.join(path, "saved-filters.json"), "w") as f:
            f.write("[]")

    if not os.path.exists(os.path.join(path, "actions.json")):
        with open(os.path.join(path, "actions.json"), "w") as f:
            f.write("[]")

    if not os.path.exists(os.path.join(path, "mtime.json")):
        with open(os.path.join(path, "mtime.json"), "w") as f:
            f.write("\{\}")

    metadata = {
        "folders": [],
        "smartFolders": [],
        "quickAccess": [],
        "tagsGroups": [],
        "modificationTime": int(time.time() * 1000),
        "applicationVersion": "4.0.0",
    }

    if not os.path.exists(os.path.join(path, "metadata.json")):
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(metadata, f)

# roaming folder
settings_path = os.path.join(os.getenv("APPDATA"), "Eagle", "Settings")

def update_library_pathes(pathes: typing.Union[dict, typing.List[str]]):
    if isinstance(pathes, list):
        with open(settings_path, "r") as f:
            settings = json.load(f)
    elif isinstance(pathes, dict):
        settings = pathes
    else:
        raise ValueError("pathes must be a list or a dict")

    settings["libraryHistory"] = pathes

    with open(os.path.join(settings_path, "settings.json"), "w") as f:
        json.dump(settings, f)

def add_library_path(path: str):
    with open(settings_path, "r") as f:
        settings = json.load(f)

    settings["libraryHistory"].append(path)

    update_library_pathes(settings)

def remove_library_path(path: str):
    with open(settings_path, "r") as f:
        settings = json.load(f)

    settings["libraryHistory"].remove(path)

    update_library_pathes(settings)

def is_eagle_library(path : str):
    if not os.path.exists(os.path.join(path, "metadata.json")):
        return False

