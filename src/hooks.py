import importlib.util
import os

import status

def post_inst(package):
    status.status("Loading hooks")
    print("(1/?) Loading hooks")

    hooks_file = f"/etc/car/post-inst-hooks"

    if not os.path.exists(hooks_file):
        print(f"No hooks file found at {hooks_file}")
        return

    with open(hooks_file, "r") as f:
        hooks = [line.strip() for line in f if line.strip()]

    steps = 1 + len(hooks) * 2
    step_counter = 1

    for i, hook_path in enumerate(hooks, start=1):
        step_counter += 1
        print(f"({step_counter}/{steps}) Loading hook {hook_path}")
        spec = importlib.util.spec_from_file_location(f"hook_{i}", hook_path)
        hook = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hook)

        step_counter += 1
        print(f"({step_counter}/{steps}) Running hook {hook_path}")
        hook.run(package)
