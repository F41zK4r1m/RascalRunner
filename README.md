# RascalRunner ㊙️

RascalRunner is a command-line red teaming tool designed to deploy malicious workflows to a Github repository covertly. It creates a temporary branch, uploads your workflow file, executes it, captures the logs, and then automatically cleans up all artifacts - including the temporary branch, workflow runs, and any deployments. This makes it ideal for testing runner-based attacks, secrets leaking, or OIDC abuse without alerting blue team to your actions. 

The tool requires a GitHub personal access token with `repo` and `workflow` permissions to function properly. New Github tokens have not been tested.

Check out the sister repository, RascalRunner Workflows, for some example workflows. Please keep in mind that RascalRunner is an advanced tool and you can easily mess up deployment and get caught if you don't know what you're doing.

## Usage


## Todo

TODO: things to make configurable
- add job and workflow ids to verbose logging
- tmp branch name
- workflow file rename
- commit message
- double commit
- max workflow run time
- workflow and job file automatic naming based on existing workflows
- new git username and email - steal from previous commit in repo?