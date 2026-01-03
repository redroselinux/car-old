import os

from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn

import umbrella.autocorrect_package as Autocorrect
from status import status

console = Console()


def main(package):
    autocorrected = Autocorrect.main(package)
    if autocorrected != package:
        package = autocorrected

    if not os.path.exists("/etc/repro.car"):
        status("No repro.car file. Creating", "warn")
        os.makedirs("/etc/car", exist_ok=True)
        open("/etc/repro.car", "w").close()
        return False

    with open("/etc/repro.car") as f:
        repro = f.read()

    if package not in repro:
        status(f"Target not found: {package}", "error")
        return False

    for i in repro.splitlines():
        if i.startswith(package):
            repro = repro.replace(i, "")

    with open("/etc/repro.car", "w") as f:
        f.write(repro)

    status(f"Uninstalling {package}...", "info")

    delete_files = []

    if os.path.isfile(f"/etc/car/saves/{package}"):
        with open(f"/etc/car/saves/{package}", "r") as f:
            delete_files = f.read().splitlines()

    # +1 to account for /usr/bin/{package}
    total = len(delete_files) + 1

    status("Progress:")

    with Progress(
        TextColumn("{task.completed}/{task.total}"),
        BarColumn(),
    ) as progress:
        task = progress.add_task("Deleting", total=total)

        for i in delete_files:
            os.system(f"rm -rf {i}")
            progress.advance(task)

        os.system(f"rm -f /usr/bin/{package}")
        progress.advance(task)
