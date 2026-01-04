import os

import status


def main():
    if not os.path.isdir("/etc/car"):
        return True
    else:
        return False
