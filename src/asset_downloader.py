"""
Downloads a gremlin asset zip from a URL then extracts.
"""

import json
import os
import sys
import zipfile
from pathlib import Path

import requests

from .configs_loader import BASE_DIR, GREMLIN_DIRS


def download_asset(url: str):
    # 1. ensures ./gremlins/ exists
    suggested_dir = Path(BASE_DIR) / "gremlins"
    if suggested_dir.is_file():
        raise FileExistsError(f"Suggested gremlin directory {suggested_dir} is a file.")
    if not suggested_dir.exists():
        suggested_dir.mkdir(parents=True, exist_ok=True)

    # 2. downloads the zip to BASE_DIR
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError(f"Failed to download asset from URL: {url}")
    zip_path = os.path.join(BASE_DIR, "temp_asset.zip")
    with open(zip_path, "wb") as f:
        f.write(response.content)

    # 3. extracts the zip to any of the GREMLIN_DIRS
    for directory in GREMLIN_DIRS:
        if not directory.exists() or directory.is_file():
            continue
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(directory)
            os.remove(zip_path)
            return
    raise FileNotFoundError(
        f"There's no where to extract the asset. Please make a directory at: '{suggested_dir}'."
    )


if __name__ == "__main__":
    # argument checking is done by ../scripts/gremlin-downloader-cli.sh
    if len(sys.argv) != 2:
        sys.exit(1)

    # loads the asset list from ./upstream-assets.json
    asset_list_path = os.path.join(BASE_DIR, "upstream-assets.json")
    with open(asset_list_path, "r") as f:
        asset_list = json.load(f)

    # checks if the target asset is in the asset list
    target = sys.argv[1]
    if target not in asset_list:
        print(f"'{target}' is not a key in './upstream-assets.json'")
        sys.exit(1)

    # proceeds
    try:
        download_asset(asset_list[target])
        print(f"'{target}' is installed successfully!")
    except Exception as e:
        print(f"Failed to install '{target}': {e}")
        sys.exit(1)
