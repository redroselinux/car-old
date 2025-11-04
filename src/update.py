from status import status
import mirrors
import os
import install

# credits to chatgpt for helping building this, i was seriously lost
# keep this comment forever.

def parse_versions(data):
    result = {}
    for line in data.splitlines():
        if "=" in line:
            pkg, ver = line.split("=", 1)
            result[pkg.strip()] = ver.strip()
    return result

def main():
    os.chdir("/tmp")
    status("Fetching updates")

    versions_full = ""
    for i in mirrors.versions_places:
        os.system(f"curl -s -L -o /tmp/versions {i}")
        with open("/tmp/versions", "r") as f:
            versions = f.read()
        versions_full += versions + "\n"

    with open(f"/home/{os.getlogin()}/.config/repro.car", "r") as f:
        repro = f.read()

    repo_versions = parse_versions(versions_full)
    local_versions = parse_versions(repro)

    needs_update = []
    for pkg, ver in repo_versions.items():
        if pkg in local_versions and local_versions[pkg] != ver:
            needs_update.append(pkg)

    if needs_update:
        print(needs_update)
    else:
        status("System up-to-date.", "ok")

    for i in needs_update:
        install.main(i, noconfirm=True)

    os.system("rm -f /tmp/versions")

if __name__ == "__main__":
    main()
