import importlib.util
import os

import status


def post_inst(package):
    status.status("Running hooks")

    hooks_file = f"/etc/car/post-inst-hooks"

    if not os.path.exists(hooks_file):
        print(f"No hooks file found at {hooks_file}")
        return

    # read what hooks to run
    with open(hooks_file, "r") as f:
        hooks = [line.strip() for line in f if line.strip()]

    steps = len(hooks)
    step_counter = 1

    for i, hook_path in enumerate(hooks, start=1):
        # load the hook
        spec = importlib.util.spec_from_file_location(f"hook_{i}", hook_path)
        hook = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hook)

        # run
        print(f"({step_counter}/{steps}) Running hook {hook_path}")
        step_counter += 1
        hook.run(package)
