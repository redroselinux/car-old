import argparse
import install
import delete
import update
import search
import updatelist
import init
import lspkgs
import info

parser = argparse.ArgumentParser(description="A simple package manager")
subparsers = parser.add_subparsers(dest="command", required=True)

# install
p_install = subparsers.add_parser("get", help="Install a package")
p_install.add_argument("package", help="Package to install")
p_install.add_argument(
    "--noconfirm",
    action="store_true",
    help="Install without confirmation"
)

# delete
p_delete = subparsers.add_parser("delete", help="Uninstall a package")
p_delete.add_argument("package", help="Package to delete")

# update
p_update = subparsers.add_parser("update", help="Update system")

# search
p_search = subparsers.add_parser("search", help="Search for a package")
p_search.add_argument("package", help="Package to search for")

# updatelist
p_updatelist = subparsers.add_parser("updatelist", help="Update packagelist")

# init
p_init = subparsers.add_parser("init", help="Init Car")

# list
p_list = subparsers.add_parser("list", help="List installed packages")

# info
p_info = subparsers.add_parser("info", help="Info about a package")
p_info.add_argument("package", help="Package to show")

args = parser.parse_args()

if args.command == "get":
    install.main(noconfirm=args.noconfirm, package=args.package)
elif args.command == "delete":
    delete.main(args.package)
elif args.command == "update":
    update.main()
elif args.command == "search":
    search.main(args.package)
elif args.command == "updatelist":
    updatelist.main()
elif args.command == "init":
    init.main()
elif args.command == "list":
    lspkgs.main()
elif args.command == "info":
    info.main(args.package)
