# dbt Cloud Job Poller

A Python CLI tool to poll dbt Cloud jobs and send system (macOS) notifications about their status.

Here is why I put this together:
- Some large dbt projects have many developers trying to merge into production. Usually, there is a merge queue to organize and sync pushes to minimize confusion, conflicts, and bugs.
- While being at the front of the queue, your dev branch may need to be synced with main
- This kicks off a CI job and sometimes, that CI job can run for a long time!
- During that time, you work and do other thing; however, still remembering that there is a queue that you are holding up
- Because of this it's important to periodically check the CI job build (usually manually)
- I dont have admin rights to Slack and our Slack workspace has a dedicated `#dbt-alerts` that I cannot chainge or add to
  - It takes too much process to ask to authorize an app in Slack and then ask the dbt Cloud Admins to create another integration that utilizes the Slack webhook, yadayadayada
  - I can add email notifs to Slack or my Inbox but those are for ALL CI jobs and there's too much noise and it ends up being unhelpful
  - So basically, Slack and Email notifications were off the table for me
- This is still a WIP in progress but the idea is simple:
  - With a dbt developer PAT and Job ID, be able to target your specific CI job that you care about, and then get notified on your laptop once it's done
  - THAT'S IT !

## Features

- Poll dbt Cloud jobs and monitor their status
- Cute terminal output with color-coded status updates 
- System notifications for job completion (aka terminal sends alerts to macOS notification center)
- Configurable polling interval
- Somewhat detailed job status information once complete

## Project Structure

```
dbt-heartrate/
├── src/
│   ├── poll_dbt_job/
│   │   └── __init__.py  (main script)
│   └── utils/
│       ├── __init__.py
│       ├── dbt_cloud_api.py  (dbt Cloud API interactions)
│       └── os_notifs.py      (mac os notifs)
├── pyproject.toml
└── README.md
```

## Prerequisites

- Python 3.8 or higher
- dbt Cloud account with API access
- macOS (for system notifications)

## Installation

1. Clone the repository:
```bash
git clone git remote add origin git@github.com:jairus-m/dbt-heartbeat.git
cd dbt-heartrate
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Configuration

Create a `.env` file in the project root with your DBT Cloud credentials:
```
DBT_CLOUD_API_KEY=your_api_key
DBT_CLOUD_ACCOUNT_ID=your_account_id
```

## Usage

Poll a DBT Cloud job:
```bash
poll-dbt-job <job_run_id> [--log-level LEVEL] [--poll-interval SECONDS]
```

### Arguments

- `job_run_id`: The ID of the DBT Cloud job run to monitor
- `--log-level`: Set the logging level (default: INFO)
  - Choices: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `--poll-interval`: Time in seconds between polls (default: 30)

### Example

```bash
# Poll job with default settings
poll-dbt-job 123456

# Poll job with debug logging and 15-second interval
poll-dbt-job 123456 --log-level DEBUG --poll-interval 15
```

## Development

The project uses a `src/` layout, which is a Python packaging best practice that:
- Prevents import confusion during development
- Ensures consistent behavior between development and installed versions
- Makes testing more reliable

### Key Components

- `src/poll_dbt_job/`: Main package containing the CLI interface
- `src/utils/`: Utility modules for API interactions and notifications
  - `dbt_cloud_api.py`: Handles DBT Cloud API communication
  - `os_notifs.py`: Manages system notifications
