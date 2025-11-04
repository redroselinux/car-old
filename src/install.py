import os
import importlib.util
from rich.console import Console
import sys
from status import status
import mirrors
import hooks
import get_package_list
import umbrella.autocorrect_package as Autocorrect

# init rich console
console = Console()

def main(package, noconfirm=False):
    # first check if the name is correct, autocorrect if not
    # using umbrella/autocorrect_package.py (unlicense)
    autocorrected = Autocorrect.main(package)
    print(autocorrected)
    if autocorrected != package:
        package = autocorrected
    
    # save time fetching scripts, check if the package is in lists quickly
    if get_package_list.main(package) != True:
        return False
    
    # main
    try:
        # save installed package
        repro_path = "/home/" + os.getlogin() + "/.config/repro.car"

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
        status("Going to /tmp", "info")
        os.chdir("/tmp/")

        # fetch all repos for the install script
        found = False

        for mirror in mirrors.install_script_places:
            url = f"{mirror.rstrip('/')}/{package}/install_script"
            status(f"Trying {url}", "info")

            result = os.system(f"curl -s -L -o install_script.py {url}")

            with open("install_script.py", "r") as f:
                script = f.read()

            # github returns 404: Not Found in case the file does not exist,
            # so handle that case too
            if script != "404: Not Found":
                status(f"Successfully fetched install script from: {url}", "success")
                found = True
                break
            else:
                status(f"Failed to fetch from: {url}", "warning")

        if not found:
            status("Failed to fetch install script from all mirrors", "error")
            exit()

        status("Reading install_script.py", "info")

        # import the script as a python library
        spec = importlib.util.spec_from_file_location("install_script", "/tmp/install_script.py")
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
            return
        elif installed_version is not None and installed_version != script_version:
            status(f"New version available for {package}: {installed_version} -> {script_version}. Reinstalling.", "warn")
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
            console.print("::", style="blue bold", end=" ")
            sure = input("Install dependencies and build? (Y/n) ")
            if sure not in ("", "y", "Y"):
                return

        # install deps
        try:
            status("Installing dependencies", "ok")
            install_script.deps()
        except Exception:pass

        # build
        try:
            status("Building", "ok")
            install_script.build()
        except Exception:pass

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

        installed_versions[package] = script_version
        write_installed_versions(repro_path, installed_versions)

        hooks.post_inst(package)

        # postinst hook
        if hasattr(install_script, "postinst"):
            install_script.postinst()

        # clean up
        status("Cleaning up")
        os.system("rm -f /tmp/install_script.py")
    except Exception:
        # crash, print exception and exit
        console.print("::", style="red", end=" ")
        console.print("Unhandled exception")
        console.print_exception()
        sys.exit(1)
    except KeyboardInterrupt:
        # keyboard interrupt, suggest cleaning up
        status("Installation interrupted", "error")
        status("There might be some files that were installed, but not removed. You can remove them manually.", "warn")
        status("If you want to remove them, run the following command:", "warn")
        status("sudo car delete " + package, "warn")
        sys.exit(1)
