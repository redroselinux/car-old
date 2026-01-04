import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

# mirrors config (written only if missing)
mirrors = """:main:
install_script = https://raw.githubusercontent.com/redroselinux/car-binary-storage/main/
packagelist = https://raw.githubusercontent.com/redroselinux/car/main/existing-packages.txt
versions = https://raw.githubusercontent.com/redroselinux/car-binary-storage/main/existing-packages-versions.txt
:end:

:core:
install_script = https://raw.githubusercontent.com/redroselinux/car-coreutils-repo/main/
packagelist = https://raw.githubusercontent.com/redroselinux/car-coreutils-repo/main/existing-packages.txt
versions = https://raw.githubusercontent.com/redroselinux/car-coreutils-repo/main/existing-packages-versions.txt
:end:
"""

# write mirrors only if they do not exist
for path in ["/etc/mirrors.car", os.path.expanduser("~/.config/mirrors.car")]:
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(mirrors)

install_script_places = []  # list of (repo, url)
packagelist_places = []  # list of (repo, url)
versions_places = []  # list of (repo, url)
repos = []

current_repo = None
current_data = {}

# parse mirrors config
for line in mirrors.strip().splitlines():
    line = line.strip()

    if line.startswith(":") and line.endswith(":") and line != ":end:":
        current_repo = line.strip(":")
        repos.append(current_repo)
        current_data = {}

    elif line == ":end:":
        if "install_script" in current_data:
            install_script_places.append((current_repo, current_data["install_script"]))
        if "packagelist" in current_data:
            packagelist_places.append((current_repo, current_data["packagelist"]))
        if "versions" in current_data:
            versions_places.append((current_repo, current_data["versions"]))
        current_repo = None
        current_data = {}

    elif current_repo and "=" in line:
        key, value = line.split("=", 1)
        current_data[key.strip()] = value.strip()


def fetch_one(repo, url):
    print("fetch " + url)
    try:
        result = subprocess.run(
            ["curl", "-fsSL", url],
            capture_output=True,
            text=True,
            check=True,
        )
        packages = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return [f"{repo}/{pkg}" for pkg in packages]
    except subprocess.CalledProcessError:
        return []


def fetch_all_packages(packagelist_places, max_threads=8):
    all_packages = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        results = executor.map(
            lambda x: fetch_one(x[0], x[1]),
            packagelist_places,
        )
        for r in results:
            all_packages.extend(r)
    return all_packages
