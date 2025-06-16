# dbt-heartbeat

A CLI tool to monitor individual dbt Cloud run jobs and receive Slack or OS notifications when they complete.

## Why This Exists

Developers working with large dbt projects and merge queues often wait for long-running CI jobs. This tool solves two problems:

1. **Manual Monitoring**: Instead of repeatedly checking job status or working on other things and forgetting about your dbt job and holding up the merge queue, automatically get notified when your specific run job completes.
2. **Notification Control**: AFAIK, dbt Cloud does not have notifications for job-specific runs. You can get notifications for all jobs of a specific environment/deployment, but not for specific runs within those environment/deployment jobs (i.e your own CI jobs in a staging environment).

## Prerequisites

- Python >= 3.8
- `uv` (Python package manager)
- dbt Cloud account with API access ([via the dbt developer PAT](https://docs.getdbt.com/docs/dbt-cloud-apis/user-tokens#create-a-personal-access-token))
- Environment variables:
  - `DBT_CLOUD_ACCOUNT_ID`
  - `DBT_CLOUD_API_KEY`
  - `SLACK_WEBHOOK_URL`
    - Only needed if posting notifications to Slack (need a valid Slack App with an authorized webhook URL)
      - [Slack Docs on Creating an Incoming Webook URL](https://api.slack.com/messaging/webhooks)
    - Default behavior of `dh` is to post to OS notifications


__NOTE:__ While `uv` is the recommended method for installing `dbt-heartbeat`, you can also install it using `pip install`. However, when installing with `pip`, you are responsible for managing your Python virtual environment and ensuring that the directory containing the executable is included in your system's `PATH`. In contrast, when using `uv` no additional environment configuration is required, and the executable is automatically made available in your `PATH` for immediate use.

## Installation
1. `brew install uv`
2. `uv tool install dbt-heartbeat`
3. Add environment variables to your `.zshrc` shell configuration file:
    ```bash
    # Paste in your .zshrc file (Mac: /Users/<user_name>/.zshrc)
    export DBT_CLOUD_ACCOUNT_ID=<dbt_cloud_account_id> 
    export DBT_CLOUD_API_KEY=<dbt_cloud_pat> 
    export SLACK_WEBHOOK_URL=<webhook_url>
    ```
4. Run `dh <run_job_id> --slack`

### Version Upgrade:
```bash
# Check for latest version
dh --version

# Upgrade to the latest version
uv tool upgrade dbt-heartbeat
```

## Usage

For help:
```bash
dh --help
```

### Arguments

- `job_run_id`: The ID of the dbt Cloud job run to monitor
- - `--slack` or `-s`: Send notifications to Slack (requires SLACK_WEBHOOK_URL environment variable)
- `--poll-interval`: Time in seconds between polls (default: 30)
- `--log-level`: Set the logging level (default: INFO)
  - Choices: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `--version`: Checks for the latest version and prints the current version

### Example

```bash
# Poll run job with default settings and send notification to system OS
dh 123456

# Poll run job with default settings and send notification to Slack
dh 123456 --slack

# Poll run job with debug logging and 15-second interval and send notification to Slack 
dh 123456 --s --log-level DEBUG --poll-interval 15
```
__Note:__ You can find the `<job_run_id>` in the dbt Cloud UI:
- In the job run details page, look for `Run #<job_run_id>` in the header of each run
- Or from the URL when viewing a job run: `https://cloud.getdbt.com/deploy/<account_id>/projects/<project_id>/runs/<job_run_id>`


#### Terminal Output

<img width="1471" alt="Screenshot 2025-05-15 at 7 47 02 AM" src="https://github.com/user-attachments/assets/84e60b52-60c9-450a-b4c3-3eb9fb7318c6" />

#### Slack App Notification
<img width="1336" alt="Screenshot 2025-06-16 at 10 52 12 AM" src="https://github.com/user-attachments/assets/8e5d62b3-a454-42c8-a232-7267ae1e702d" />


#### Note on Internal Slack App for Webhook URL Generation
- A single app can be shared within a workspace so that end users don't have to repeteadly create a Slack app from scratch just to generate their own unique webhook URL
- As an example, I created a `dbt-heartbeat` Slack App in my company's workspace and authorized the incoming webhook URL to post messages to the Slack App's Direct Message
  - This app can be reused and shared with others to configure their own unique webhook URLs for posting messages from `dh`
