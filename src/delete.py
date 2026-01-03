import os
import sys

from rich.console import Console

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

    with open("", "w") as f:
        f.write(repro)

    status(f"Uninstalling {package}...", "info")
    try:
        if os.system(f"sudo rm -f /usr/bin/{package}") != 0:
            status(f"Failed to uninstall {package}", "error")
            return False
        status(f"Successfully uninstalled {package}", "ok")
        return True
    except Exception:
        console.print("::", style="red", end=" ")
        console.print("Unhandled exception")
        console.print_exception()
        return False
