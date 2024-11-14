import argparse
import sys
import logging
from .github_wrapper import GithubWrapper
from .rascalrunner import RascalRunner
from .reconrunner import ReconRunner

ascii_banner = """
 ██▀███   ▄▄▄        ██████  ▄████▄   ▄▄▄       ██▓        ██▀███   █    ██  ███▄    █  ███▄    █ ▓█████  ██▀███  
▓██ ▒ ██▒▒████▄    ▒██    ▒ ▒██▀ ▀█  ▒████▄    ▓██▒       ▓██ ▒ ██▒ ██  ▓██▒ ██ ▀█   █  ██ ▀█   █ ▓█   ▀ ▓██ ▒ ██▒
▓██ ░▄█ ▒▒██  ▀█▄  ░ ▓██▄   ▒▓█    ▄ ▒██  ▀█▄  ▒██░       ▓██ ░▄█ ▒▓██  ▒██░▓██  ▀█ ██▒▓██  ▀█ ██▒▒███   ▓██ ░▄█ ▒
▒██▀▀█▄  ░██▄▄▄▄██   ▒   ██▒▒▓▓▄ ▄██▒░██▄▄▄▄██ ▒██░       ▒██▀▀█▄  ▓▓█  ░██░▓██▒  ▐▌██▒▓██▒  ▐▌██▒▒▓█  ▄ ▒██▀▀█▄  
░██▓ ▒██▒ ▓█   ▓██▒▒██████▒▒▒ ▓███▀ ░ ▓█   ▓██▒░██████▒   ░██▓ ▒██▒▒▒█████▓ ▒██░   ▓██░▒██░   ▓██░░▒████▒░██▓ ▒██▒
░ ▒▓ ░▒▓░ ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░ ▒▒   ▓▒█░░ ▒░▓  ░   ░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ░ ▒░   ▒ ▒ ░ ▒░   ▒ ▒ ░░ ▒░ ░░ ▒▓ ░▒▓░
  ░▒ ░ ▒░  ▒   ▒▒ ░░ ░▒  ░ ░  ░  ▒     ▒   ▒▒ ░░ ░ ▒  ░     ░▒ ░ ▒░░░▒░ ░ ░ ░ ░░   ░ ▒░░ ░░   ░ ▒░ ░ ░  ░  ░▒ ░ ▒░
  ░░   ░   ░   ▒   ░  ░  ░  ░          ░   ▒     ░ ░        ░░   ░  ░░░ ░ ░    ░   ░ ░    ░   ░ ░    ░     ░░   ░ 
   ░           ░  ░      ░  ░ ░            ░  ░    ░  ░      ░        ░              ░          ░    ░  ░   ░     
                            ░                                                                                     
https://github.com/nopcorn/rascalrunner
"""

logging.basicConfig(
    format="%(asctime)s %(message)s",
    stream=sys.stdout, 
    level=logging.INFO
)

def main():
    parser = argparse.ArgumentParser(description="Run and test github workflows")
    subparsers = parser.add_subparsers(dest='mode', help='Operating mode')
    
    recon_parser = subparsers.add_parser('recon', help='Analyze a GitHub token for access and permissions')
    recon_parser.add_argument("-v", "--verbose", help="Tell me what that little rascal is doing", action="store_true")
    recon_parser.add_argument("-a", "--auth", help="Github authentication token to run the recon with", required=True)
    recon_parser.add_argument("--show-all", help="Show all possible target repositories, even if the PAT doesn't have the right permissions", action="store_true")

    run_parser = subparsers.add_parser('run', help='Run and test a workflow')
    run_parser.add_argument("-v", "--verbose", help="Tell me what that little rascal is doing.", action="store_true")
    run_parser.add_argument("-a", "--auth", help="Github authentication token. Used to clone the repository and remove the workflow run.", required=True)
    run_parser.add_argument("-t", "--target", help="The repository to clone and insert the workflow into (ie, nopcorn/rascalrunner).", required=True)
    run_parser.add_argument("-w", "--workflow-file", help="Workflow file to commit and run.", required=True)
    
    args = vars(parser.parse_args())

    print(ascii_banner)

    if args.get("verbose"):
        logging.getLogger().setLevel(logging.DEBUG)

    wrapper = GithubWrapper(args["auth"])

    if args["mode"] == "recon":
        recon = ReconRunner(wrapper, show_all=args['show_all'])
        recon.run()
    elif args["mode"] == "run":
        rascal = RascalRunner(args["target"], args["workflow_file"], wrapper)
        rascal.run()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()