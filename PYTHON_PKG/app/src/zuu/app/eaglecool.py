import os
import time
import json

def new_ver4_library(path: str):
    os.makedirs(path, exist_ok=True)

    assert os.path.isdir(path)

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