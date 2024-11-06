from github import Github, Auth
import requests
import logging
import re
import time

class GithubWrapper:
    def __init__(self, token):
        self._token = token

        # _login() will set up the Github object
        self._github, self._token_scopes = self._login()

        # set up a session for the manual API calls - we manage rate limiting here too
        self.config = {
            'headers': {
                'Authorization': f'token {self._token}',
                'Accept': 'application/vnd.github.v3+json'
            },
            'api_url': 'https://api.github.com',
            'max_retries': 3,
            'retry_delay': 5 # seconds
        }
        self.session = requests.Session()
        self.session.headers.update(self.config['headers'])


    @property
    def github(self):
        return self._github
   
    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        pattern = r"^ghp_[a-zA-Z0-9]{36}$"
        if not re.match(pattern, token):
            raise Exception("Token provided doesn't seem to be valid. It should match {pattern}.")
        self._token = token

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
            raise Exception(f"Workflow access isn't allowed with the provided token. RascalRunner won't be able to pull logs or clean up the workflow run. RascalRunner won't work with this token.")
        
        logging.debug("Login to Github successful")
        logging.debug(f"Auth token has scopes: {oauth_scopes}")

        self._token_scope = oauth_scopes
        self._github = gh
        return gh, oauth_scopes

    def api_call(self, method, url, **kwargs):
        for attempt in range(self.config['max_retries']):
            try:
                response = self.session.request(method, url, **kwargs)
                
                if response.status_code == 429:  # rate limit exceeded
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    sleep_time = max(reset_time - time.time(), 0) + 1
                    logging.warning(f"Rate limit exceeded. Sleeping for {sleep_time:.2f} seconds.")
                    time.sleep(sleep_time)
                    continue
                else:
                    return response

            except requests.exceptions.RequestException as e:
                if attempt == self.config['max_retries'] - 1:
                    logging.error(f"Error making request to {url}: {str(e)}")
                    raise
                logging.warning(f"Request failed. Retrying in {self.config['retry_delay']} seconds...")
                time.sleep(self.config['retry_delay'])
        
        raise requests.exceptions.RequestException("Max retries exceeded")

