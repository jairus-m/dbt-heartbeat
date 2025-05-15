# dbt Cloud Job Poller

A Python CLI tool to poll dbt Cloud jobs and send system (macOS) notifications about their status.

## Why This Exists

When working with large dbt projects, developers often need to wait for CI jobs to complete after syncing their branches with main. This tool solves two key problems:

1. **Manual Monitoring**: Instead of repeatedly checking job status, get notified when your specific job completes
2. **Notification Control**: Since Slack/email notifications are either unavailable for notifs specific to a run (job_id) or too noisy if set for all CI alerts, this provides targeted notifications just for your target jobs.

Simply provide your dbt Cloud PAT and Job ID, and get notified on your laptop when the job finishes.

## Features

- Poll dbt Cloud jobs and monitor their status
- Cute terminal output with color-coded status updates 
- System notifications for job completion (aka terminal sends alerts to macOS notification center)
- Configurable polling interval
- Somewhat detailed job status information once complete

## Project Structure

```bash
dbt-heartrate/
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
- dbt Cloud account with API access (via developer PAT)
- macOS (for system notifications)

## Installation

1. Clone the repository:
```bash
git clone git remote add origin git@github.com:jairus-m/dbt-heartbeat.git
cd dbt-heartrate
```

2. Create and activate a virtual environment:
```bash
uv sync
source .venv/bin/activate
```

3. Install the package in development mode:
```bash
uv pip install -e .
```

## Configuration

Create a `.env` file in the project root with your dbt Cloud credentials:
```
DBT_CLOUD_API_KEY=your_api_key
DBT_CLOUD_ACCOUNT_ID=your_account_id
```
Or export them directly in your terminal session:
```
export DBT_CLOUD_API_KEY=your_dbt_cloud_api_key
export DBT_CLOUD_ACCOUNT_ID=your_dbt_cloud_account_id
```

## Usage

For help:
```bash
dh --help
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

#### Bash Output

<img src="images/Screenshot 2025-05-15 at 7.47.02 AM.png" width="800">

#### macOS Notification

<img src="images/Screenshot 2025-05-15 at 7.28.22 AM.png" width="600">

### Future Work & Limitations
1. The dbt CLoud API has a [runs/ endpoint](https://docs.getdbt.com/dbt-cloud/api-v2#/operations/List%20Runs) that's supposed to have a `run_steps` key within the `data` dict.
    - This would allow for dynamic output of which dbt command is running
    - Unforunately, with dbt Cloud API v2, that endpoint has been unstable and is no longer populated leading to missing functionality for a better CLI status output
2. I focused the notifications for my MacBook and thus, have used `pync` which is a wrapper for `terminal-notifer` for macOS system notifications
    - So unfortuntaely, the current version does not support notifications for other OS systems (the CLI output should still work!)