# dbt Cloud Job Poller

A CLI tool to poll dbt Cloud jobs and send system (macOS) notifications about their status.

## Why This Exists

When working with large dbt projects that utilize a merge queue, developers often need to wait for CI jobs to complete after syncing their branches with main before pushing changes. This tool solves two key problems:

1. **Manual Monitoring**: Instead of repeatedly checking job status or working on other things and forgetting about your dbt job and holding up the merge queue, get notified when your specific job completes.
2. **Notification Control**: AFAIK, dbt Cloud does not have notifications for job-specific runs. You can get notifications for all jobs of a specific environment/deployment, but not for specific ones (i.e your own CI jobs in a staging environment).

This tool solves for these! All you need is a dbt Cloud PAT, dbt Cloud account ID, and a specific Job ID, and you'll be able to watch the status of the jobn in your terminal and get notified in the macOS notification center when the job finishes.

## Features

- Poll dbt Cloud jobs and monitor their status
- Cute terminal output with color-coded status updates xD
- System notifications for job completion (aka terminal sends alerts to macOS notification center)
- Configurable polling interval
- Can control the log level of the CLI output
- Somewhat detailed job status information once complete haha

## Project Structure

```bash
dbt-heartbeat/
├── src/
│   ├── dbt_heartbeat.py      # Main Python module/entrypoint
│   └── utils/
│       ├── __init__.py
│       ├── dbt_cloud_api.py  # dbt Cloud API interactions
│       └── os_notifs.py      # macOS notifs
├── pyproject.toml
└── README.md
```

## Prerequisites

- Python 3.8 or higher
- dbt Cloud account with API access ([via the dbt developer PAT](https://docs.getdbt.com/docs/dbt-cloud-apis/user-tokens#create-a-personal-access-token))
- macOS (for system notifications)

__Note:__ This package is designed to be installed using `uv`, a modern Python package installer and resolver. While `uv` offers improved performance and dependency management capabilities, some project dependencies (like `pync`) still rely on legacy build artifacts that aren't fully compatible with modern Python packaging standards. As a result, installation via `pip` is not currently supported, but you can use `uv` with pip-compatible commands like `uv pip install dbt-heartbeat`. The following section will guide you through the installation process using `uv`!

## Installation - For General Use
1. Add dbt environment variables to your `~/.zshrc` directory
   - Refer to the guide below for global export of environment variables for all terminal sessions
   - Other options are noted as well for non-global export of environment variables
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1)
    - Check the installation with `uv --version`
3. Global installation of `dbt-heartbeat`:
    - Run `uv tools install dbt-heartbeat`
    - This will make `dbt-heartbeat` globally available on all terminal sessions
4. Check the installation with `dh --version`
5. Poll a job!
    - `dh <job_id>`

## Installation - For Contributors

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1)

2. Clone the repository:
```bash
git clone git@github.com:jairus-m/dbt-heartbeat.git
cd dbt-heartbeat
```

3. Add required environment variables in a `.env` file within your local repository's root directory

4. Create and activate the virtual environment:
```bash
uv venv # initialize
uv sync # sync
source .venv/bin/activate # activate
```

5. Run `dh <job_id> --log-level DEBUG`


## Configuratin Guide for Environment Variables

#### For global export
If you want to persist the environment variables in all terminal sessions without having to utilize a `.env` file or manually exporting the variables in your terminal session, you can add the export commands to your `~/.zshrc` directory. (persisted)
```bash
# in ~/.zshrc
export DBT_CLOUD_API_KEY=your_dbt_cloud_api_key
export DBT_CLOUD_ACCOUNT_ID=your_dbt_cloud_account_id
```

#### For using a .env file
- Create a `.env` file in the project root with your dbt Cloud credentials
- The `.env` file is scoped to the terminal session that is loaded from the same working directory (persisted in project directory)
```
# add these to a .env file at the root of your directory
DBT_CLOUD_API_KEY=your_api_key
DBT_CLOUD_ACCOUNT_ID=your_account_id
```

#### For exporting manually in the terminal
Or export them directly in your terminal session:
- Exporting is scoped to the specific terminal session you are in (ephemeral)
```
# run these in the terminal
export DBT_CLOUD_API_KEY=your_dbt_cloud_api_key
export DBT_CLOUD_ACCOUNT_ID=your_dbt_cloud_account_id
```


## Usage

For help / version:
```bash
dh --help
dh --version
```

Poll a dbt Cloud job:
```bash
dh <job_run_id> [--log-level LEVEL] [--poll-interval SECONDS]
```

### Arguments

- `job_run_id`: The ID of the dbt Cloud job run to monitor
- `--log-level`: Set the logging level (default: INFO)
  - Choices: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `--poll-interval`: Time in seconds between polls (default: 30)

### Example

```bash
# Poll job with default settings
dh 123456

# Poll job with debug logging and 15-second interval
dh 123456 --log-level DEBUG --poll-interval 15
```

#### Terminal Output

<img src="images/Screenshot 2025-05-15 at 7.47.02 AM.png" width="800">

#### macOS Notification

<img src="images/Screenshot 2025-05-15 at 7.28.22 AM.png" width="600">

### Future Work & Limitations
1. The dbt CLoud API has a [runs/ endpoint](https://docs.getdbt.com/dbt-cloud/api-v2#/operations/List%20Runs) that's supposed to have a `run_steps` key within the `data` dict.
    - This would allow for dynamic output of which dbt command is running
    - Unforunately, with dbt Cloud API v2, that endpoint has been unstable and is no longer populated leading to missing functionality for a better CLI status output
2. I focused the notifications for my MacBook and thus, have used `pync` which is a wrapper for `terminal-notifer` for macOS system notifications
    - So unfortuntaely, the current version does not support notifications for other OS systems (the CLI output should still work!)
3. Unit tests...!