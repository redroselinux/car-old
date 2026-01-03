import importlib.util
import os
import sys

from rich.console import Console

import get_package_list
import hooks
import install
import mirrors
import umbrella.autocorrect_package as Autocorrect
from status import status

# init rich console
console = Console()

# Track packages currently being installed to prevent circular dependencies
_installing = set()


def main(package, noconfirm=False):
    local = False
    # check if package is local
    if package.endswith(".car"):
        os.system(f"unzip {package}")
        os.chdir(package)
        with open("install_script.py", "r") as f:
            script = f.read()
        local = True
    # first check if the name is correct, autocorrect if not
    # using umbrella/autocorrect_package.py (unlicense)
    if not local:
        autocorrected = Autocorrect.main(package)
        if autocorrected != package:
            package = autocorrected

    # Prevent circular dependencies and infinite loops
    if package in _installing:
        return
    _installing.add(package)
    try:
        # save time fetching scripts, check if the package is in lists quickly
        if not local:
            if get_package_list.main(package) != True:
                return False

        # main
        try:
            # save installed package
            repro_path = "/etc/repro.car"

            def read_installed_versions(path):
                versions = {}
                if not os.path.isfile(path):
                    return versions
                with open(path, "r") as f:
                    for line in f.read().splitlines():
                        if not line.strip():
                            continue
                        if "=" in line:
                            name, ver = line.split("=", 1)
                            versions[name.strip()] = ver.strip()
                        else:
                            versions[line.strip()] = ""
                return versions

            def write_installed_versions(path, versions):
                lines = []
                for name, ver in versions.items():
                    if ver:
                        lines.append(f"{name}={ver}")
                    else:
                        lines.append(name)
                with open(path, "w") as f:
                    f.write("\n".join(lines) + "\n")

            # go to /tmp
            if not local:
                os.chdir("/tmp/")

                status("Fetching package")

                # fetch all repos for the install script
                found = False

                for mirror in mirrors.install_script_places:
                    url = f"{mirror.rstrip('/')}/{package}/install_script"

                    os.system(f"curl -s -L -o install_script.py {url}")

                    with open("install_script.py", "r") as f:
                        script = f.read()

                    # github returns 404: Not Found in case the file does not exist,
                    # so handle that case too
                    if script != "404: Not Found":
                        found = True
                        break
                    else:
                        pass

                if not found:
                    status("Failed to fetch install script from all mirrors", "error")
                    exit(1)

            # import the script as a python library
            spec = importlib.util.spec_from_file_location(
                "install_script", "install_script.py"
            )
            install_script = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(install_script)

            # check for version
            script_version = None
            if hasattr(install_script, "VERSION"):
                script_version = getattr(install_script, "VERSION")
            elif hasattr(install_script, "version"):
                script_version = getattr(install_script, "version")
            if script_version is None:
                script_version = ""
            else:
                script_version = script_version

            # reinstall if new version available
            installed_versions = read_installed_versions(repro_path)
            installed_version = installed_versions.get(package)
            if installed_version is not None and installed_version == script_version:
                status(f"{package} is up to date ({script_version}). Exiting.", "ok")
                status(
                    f"You can use\n   sudo car delete {package} && sudo car get {package}"
                )
                status("to reinstall it")
                return
            elif installed_version is not None and installed_version != script_version:
                status(
                    f"New version available for {package}: {installed_version} -> {script_version}. Reinstalling.",
                    "warn",
                )
            elif installed_version is None:
                if not os.path.isfile(repro_path):
                    status("No repro.car file. Creating", "warn")
                    with open(repro_path, "w") as f:
                        f.write("")

            # beforeinst hook
            if hasattr(install_script, "beforeinst"):
                install_script.beforeinst()

            # ask for confirmation
            if not noconfirm:
                status("The following packages are going to be installed:")
                if "description" not in script:
                    description = "No description defined."
                else:
                    description = install_script.description
                print(
                    f"    {package}={install_script.version} - {description}"
                )  # appending to the list did not work for some reason
                if "car_deps" in script:
                    counter = 1
                    if len(install_script.car_deps) != 0:
                        print("    dependencies: ", end="")
                        for i in install_script.car_deps:
                            if counter != len(install_script.car_deps):
                                print(f"{i}, ", end="")
                            else:
                                print(f"{i}", end="")
                        print()
                if "outdated = True" in script:
                    if (
                        package != "example"
                    ):  # example is set to be outdated for demonstration
                        status(f'The package "{package}" is outdated! ', "error")
                console.print("::", style="blue bold", end=" ")
                sure = input("Install dependencies and build? (Y/n) ")
                if sure not in ("", "y", "Y"):
                    return

            # install deps
            if "deps" in script:
                try:
                    install_script.deps()
                except Exception:
                    pass
            if "car_deps" in script:
                for i in install_script.car_deps:
                    install.main(i, noconfirm=True)

            # build
            if "build" in script:
                try:
                    install_script.build()
                except Exception:
                    pass

            # ask for confirmation
            # todo: make confirmation prompts better by mixing into one
            if not noconfirm:
                console.print("::", style="blue bold", end=" ")
                sure = input("Install? (Y/n) ")
                if sure not in ("", "y", "Y"):
                    return

            # install, required hook
            status("Installing", "ok")
            install_script.install()

            if not "DoNotWriteVersion = True" in script:
                installed_versions[package] = script_version
                write_installed_versions(repro_path, installed_versions)

            hooks.post_inst(package)

            # postinst hook
            if hasattr(install_script, "postinst"):
                install_script.postinst()

            # clean up
            os.system("sudo rm -f /tmp/install_script.py")
        except Exception:
            # crash, print exception and exit
            console.print("::", style="red", end=" ")
            console.print("Unhandled exception")
            console.print_exception()
            sys.exit(1)
        except KeyboardInterrupt:
            # keyboard interrupt, suggest cleaning up
            status("Installation interrupted", "error")
            status(
                "There might be some files that were installed, but not removed. You can remove them manually.",
                "warn",
            )
            status("If you want to remove them, run the following command:", "warn")
            status("sudo car delete " + package, "warn")
            sys.exit(1)
    finally:
        # Always remove from installing set, even if installation fails
        _installing.discard(package)
