import os
import sys
import ast
import textwrap
import mirrors

def extract_header_metadata(script_text: str) -> dict:
    info = {}
    lines = []
    for line in script_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("def ") or stripped.startswith("class "):
            break
        if stripped:
            lines.append(line)
    try:
        tree = ast.parse(textwrap.dedent("\n".join(lines)))
    except SyntaxError:
        return info
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Assign) and hasattr(node.targets[0], "id"):
            key = node.targets[0].id
            try:
                value = ast.literal_eval(node.value)
            except Exception:
                value = None
            info[key] = value
    return info

def show_pkg_info(package: str, info: dict):
    print(f"Package: {package}")
    print(f"Version: {info.get('version', 'unknown')}")
    print(f"Trusted: {info.get('trusted', 'unknown')}")
    print(f"Outdated: {info.get('outdated', 'unknown')}")
    print(f"Description: {info.get('description', 'no description provided')}")
    print("Maintainers:")
    maintainers = info.get("maintainer", [])
    if isinstance(maintainers, list) and maintainers:
        for m in maintainers:
            name = m.get("Name", "unknown")
            nick = m.get("nick", "unknown")
            email = m.get("email", "unknown")
            print(f"  - {name} ({nick}) <{email}>")
    else:
        print("  none listed")

    deps = info.get("car_deps", [])
    if isinstance(deps, list) and deps:
        print("Dependencies: " + ", ".join(deps))
    else:
        print("Dependencies: none")

def main(package: str):
    try:
        os.chdir("/tmp")

        found = False
        for mirror in mirrors.install_script_places:
            url = f"{mirror.rstrip('/')}/{package}/install_script"
            os.system(f"curl -s -L -o install_script.py {url}")

            with open("install_script.py", "r") as f:
                content = f.read()

            if content.strip() != "404: Not Found":
                found = True
                break

        if not found:
            return False

        info = extract_header_metadata(content)
        show_pkg_info(package, info)

        os.remove("/tmp/install_script.py")
        return True

    except KeyboardInterrupt:
        status("Operation cancelled", "warn")
        return False
    except Exception:
        print("Unhandled exception while fetching info:")
        import traceback
        traceback.print_exc()
        return False
