from status import status
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

try:
    with open("/home/" + os.getlogin() + "/.config/mirrors.car", "r") as f:
        mirrors = f.read()
except Exception:
    with open("/home/" + os.getlogin() + "/.config/mirrors.car", "w") as f:
        f.write(""":main:
install_script = https://raw.githubusercontent.com/redroselinux/car-binary-storage/main/
packagelist = https://raw.githubusercontent.com/redroselinux/car/main/existing-packages.txt
versions = https://raw.githubusercontent.com/redroselinux/car-binary-storage/main/existing-packages-versions.txt
:end:

:core:
install_script = https://raw.githubusercontent.com/redroselinux/car-coreutils-repo/main/
packagelist = https://raw.githubusercontent.com/redroselinux/car-coreutils-repo/main/existing-packages.txt
versions = https://raw.githubusercontent.com/redroselinux/car-coreutils-repo/main/existing-packages-versions.txt
:end:
                """)

install_script_places = []
packagelist_places = []
versions_places = []
repos = []

current_repo = None
current_data = {}

for line in mirrors.strip().splitlines():
    line = line.strip()
    if line.startswith(":") and line.endswith(":") and line != ":end:":
        current_repo = line.strip(":")
        repos.append(current_repo)
        current_data = {}
    elif line == ":end:":
        if "install_script" in current_data:
            install_script_places.append(current_data["install_script"])
        if "packagelist" in current_data:
            packagelist_places.append(current_data["packagelist"])
        if "versions" in current_data:
            versions_places.append(current_data["versions"])
        current_repo = None
        current_data = {}
    elif current_repo and "=" in line:
        key, value = line.split("=", 1)
        current_data[key.strip()] = value.strip()

def _fetch_one(url):
    print("fetch " + url)
    try:
        result = subprocess.run(
            ["curl", "-fsSL", url],
            capture_output=True,
            text=True,
            check=True
        )
        packages = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        repo_name = url.strip().split("/")[-2] if "/" in url else "unknown"
        return [f"{repo_name}/{pkg}" for pkg in packages]
    except subprocess.CalledProcessError:
        return []

def fetch_all_packages(packagelist_places, max_threads=8):
    all_packages = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        results = executor.map(_fetch_one, packagelist_places)
        for r in results:
            all_packages.extend(r)
    return all_packages
