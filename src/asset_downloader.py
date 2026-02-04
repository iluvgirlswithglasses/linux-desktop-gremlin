"""
Downloads a gremlin asset zip from a URL then extracts.
"""

import os
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
