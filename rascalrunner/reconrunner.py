import logging
import requests
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import box

class ReconRunner:

    def __init__(self, wrapper, show_all):
        self.wrapper = wrapper
        self.show_all = show_all

    def print_token_table(self):
        table = Table(title="Token Information", title_justify="left", box=box.SQUARE)
        table.add_column("Key", justify="left", no_wrap=True)
        table.add_column("Value", justify="left", no_wrap=True)

        try:
            response = self.wrapper.api_call('GET', 'https://api.github.com/user')
            if response.status_code == 200:
                user_data = response.json()
                owner_string = f"{user_data['name']} (@{user_data['login']})"
                account_type_string = f"{user_data['type']}"
                mfa_string = f"{'Yes' if user_data['two_factor_authentication'] else 'No'}"
            else:
                owner_string = account_type_string = mfa_string = f"Error fetching information (HTTP status_code {response.status_code})"

            response = self.wrapper.api_call('GET', 'https://api.github.com/user/emails')
            if response.status_code == 200:
                emails = response.json()
                email_string = f"{', '.join(email['email'] for email in emails)}"
            else:
                email_string = f"Error fetching information (HTTP status_code {response.status_code})"

            response = self.wrapper.api_call('GET', 'https://api.github.com/user/orgs')
            if response.status_code == 200:
                orgs = response.json()
                orgs_string = f"{', '.join(org['login'] for org in orgs)}"
            else:
                orgs_string = f"Error fetching information (HTTP status_code {response.status_code})"
            
            table.add_row("Owner", owner_string)
            table.add_row("Account Type", account_type_string)
            table.add_row("2FA Configured", mfa_string)
            table.add_row("Email(s)", email_string)
            table.add_row("Org(s)", orgs_string)
            table.add_row("Token Scopes", f"{', '.join(scope for scope in self.wrapper._token_scope)}")

            console = Console()
            console.print(table)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching token information: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")


    def print_repo_table(self):
        console = Console()
        table = Table(title="\nRepository Targets (at minimum push permissions)", title_justify="left", box=box.SQUARE)
        table.add_column("Target", justify="left", no_wrap=True)
        table.add_column("Permission(s)", justify="left", no_wrap=True)
        table.add_column("Num Secrets", justify="left", no_wrap=True)
        table.add_column("Num Runs", justify="left", no_wrap=True)
        table.add_column("Last Run Info", justify="left", no_wrap=False)

        try:
            with Live(console=console, refresh_per_second=2) as live:
                page = 1
                while True:
                    url = f"https://api.github.com/user/repos?per_page=100&page={page}"
                    response = self.wrapper.api_call('GET', url)
                    response.raise_for_status()
                    repos = response.json()
                    has_next = True if "next" in response.links else False

                    for repo in repos:
                        if repo['archived']: continue  # skip archived repos
                        if not repo['permissions']['push'] and not self.show_all: 
                            continue  # without push we can't do much
                        
                        live.update(f"Processing {repo['full_name']}...")

                        permissions = ", ".join([perm for perm, has_perm in repo['permissions'].items() if has_perm])

                        url = f"https://api.github.com/repos/{repo['full_name']}/actions/runs"
                        response = self.wrapper.api_call('GET', url)
                        runs_count = 0
                        last_run_string = ""
                        if response.status_code == 200:
                            runs_data = response.json()
                            runs_count = runs_data['total_count']
                            if runs_count > 0:
                                last_run = runs_data['workflow_runs'][0]
                                last_run_string = f"{last_run.get('display_title')} ({last_run.get('name')}) - {last_run.get('created_at')}"

                        url = f"https://api.github.com/repos/{repo['full_name']}/actions/secrets"
                        response = self.wrapper.api_call('GET', url)
                        num_secrets = 0
                        if response.status_code == 200:
                            num_secrets = response.json().get('total_count')

                        if runs_count != 0 or num_secrets != 0:
                            table.add_row(
                                repo['full_name'],
                                permissions,
                                str(num_secrets),
                                str(runs_count),
                                last_run_string
                            )
                            
                    if not has_next:
                        live.update("")
                        break
                    page += 1
            
            console.clear()
            console.print(table)
                
        except Exception as e:
            print(f"\nError during repository analysis: {str(e)}")


    def run(self):
        self.print_token_table()
        self.print_repo_table()

        
