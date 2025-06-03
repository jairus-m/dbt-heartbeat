# dbt-heartbeat

A CLI tool to monitor individual dbt Cloud run jobs and receive OS notifications when they complete.

## Why This Exists

When working with large dbt projects that utilize a merge queue, developers often need to wait for long-running CI jobs to complete after syncing their branches with main before pushing changes. This tool solves two key problems:

1. **Manual Monitoring**: Instead of repeatedly checking job status or working on other things and forgetting about your dbt job and holding up the merge queue, automatically get notified when your specific run job completes.
2. **Notification Control**: AFAIK, dbt Cloud does not have notifications for job-specific runs. You can get notifications for all jobs of a specific environment/deployment, but not for specific runs within those environment/deployment jobs (i.e your own CI jobs in a staging environment).

All you need is a dbt Cloud developer PAT, dbt Cloud account ID, and a specific job run ID, and you'll be able to watch the status of the job run in your terminal and get notified when the job finishes.

## Features

- Poll dbt Cloud job runs and monitor their status
- Cute terminal output with color-coded status updates xD
- System notifications for job completion (alerts sent to Mac/Windows OS notifications)
- Configurable polling interval
- Can control the log level of the CLI output
- Detailed job run status information once complete in CLI + system notifications

## Prerequisites

- Python 3.8 or higher
- dbt Cloud account with API access ([via the dbt developer PAT](https://docs.getdbt.com/docs/dbt-cloud-apis/user-tokens#create-a-personal-access-token))
- A Python package manager such as:
  - `uv>=0.6.11`
  - `pip>=25.1.1`


__NOTE:__ While `uv` is the recommended method for installing `dbt-heartbeat`, you can also install it using `pip install`. However, when installing with `pip`, you are responsible for managing your Python virtual environment and ensuring that the directory containing the executable is included in your system's `PATH`. In contrast, when using `uv` (particularly as described in the *For General Use* section below) no additional environment configuration is required, and the executable is automatically made available in your `PATH` for immediate use.

## Installation - For General Use
1. Add dbt environment variables to your shell configuration file (macOS defaults to `~/.zshrc`)
   - Refer to the guide below for global export of environment variables for all terminal sessions
   - Other options are noted as well for non-global export of environment variables
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1)
    - Check the installation with `uv --version`
3. Global installation:
    - Run `uv tools install dbt-heartbeat`
    - This will make `dbt-heartbeat` globally available on all terminal sessions
4. Check the installation with `dh --version`
5. Poll a job run!
    - `dh <job_run_id>`

### Upgrading:
```bash
uv tool upgrade dbt-heartbeat
```


## Configuration Guide for Environment Variables

The following environment variables are required and must be properly set:

- `DBT_CLOUD_API_KEY`: Your dbt Cloud API key (must be non-empty)
- `DBT_CLOUD_ACCOUNT_ID`: Your dbt Cloud account ID (must be non-empty)

The tool will validate these variables before starting and will notify you if any are missing or invalid.

#### For global export
If you want to persist the environment variables in all terminal sessions without having to utilize a `.env` file or manually exporting the variables in your terminal session, you can add the export commands to your shell configuration file. (persisted)
```bash
# in shell configuration file (i.e `~/.zshrc` or `~/.bashrc`)
export DBT_CLOUD_API_KEY=your_dbt_cloud_api_key
export DBT_CLOUD_ACCOUNT_ID=your_dbt_cloud_account_id
```

#### For exporting manually in the terminal
Or export environment variables directly in your terminal session:
- Exporting is scoped to the specific terminal session you are in (ephemeral)
```
# run these in the terminal
export DBT_CLOUD_API_KEY=your_dbt_cloud_api_key
export DBT_CLOUD_ACCOUNT_ID=your_dbt_cloud_account_id
```


## Usage

For help:
```bash
dh --help
```

Poll a dbt Cloud run job:
```bash
dh <job_run_id> [--log-level LEVEL] [--poll-interval SECONDS]
```

__Note:__ You can find the `<job_run_id>` in the dbt Cloud UI:
- In the job run details page, look for `Run #<job_run_id>` in the header of each run
- Or from the URL when viewing a job run: `https://cloud.getdbt.com/deploy/<account_id>/projects/<project_id>/runs/<job_run_id>`

### Arguments

- `job_run_id`: The ID of the dbt Cloud job run to monitor
- `--log-level`: Set the logging level (default: INFO)
  - Choices: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `--poll-interval`: Time in seconds between polls (default: 30)

### Example

```bash
# Poll run job with default settings
dh 123456

# Poll run job with debug logging and 15-second interval
dh 123456 --log-level DEBUG --poll-interval 15
```

#### Terminal Output

<img width="1471" alt="Screenshot 2025-05-15 at 7 47 02 AM" src="https://github.com/user-attachments/assets/84e60b52-60c9-450a-b4c3-3eb9fb7318c6" />


#### macOS Notification

<img width="644" alt="Screenshot 2025-05-18 at 7 54 19 PM" src="https://github.com/user-attachments/assets/77d4f851-a9f7-492d-946d-a220ad536901" />


### Future Work & Limitations
The dbt CLoud API has a [runs endpoint](https://docs.getdbt.com/dbt-cloud/api-v2#/operations/List%20Runs) that's supposed to have a `run_steps` key within the `data` JSON object.
- This would allow for dynamic output of which dbt command is *currently* running
- Unfortunately, with dbt Cloud API v2, that endpoint has been unstable and is no longer populated leading to missing functionality for an enhanced CLI status output

