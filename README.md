# aws-json-dataset
Classes and methods for working with JSON data and AWS services.

## Table of Contents
- [aws-json-dataset](#aws-json-dataset)
  - [Table of Contents](#table-of-contents)
  - [Project Structure](#project-structure)
  - [Description](#description)
    - [To Do](#to-do)
      - [Next Steps](#next-steps)
    - [Ideas](#ideas)
  - [Quickstart](#quickstart)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Creating a Python Virtual Environment](#creating-a-python-virtual-environment)
    - [Notebook Setup](#notebook-setup)
    - [Environment Variables](#environment-variables)
    - [AWS Credentials](#aws-credentials)
  - [Troubleshooting](#troubleshooting)
  - [References \& Links](#references--links)
  - [Authors](#authors)

## Description
Lightweight Python package to quickly send JSON data to various AWS services including:
- SQS
- SNS
- Kinesis Firehose
<!-- - Kinesis Data Streams -->

The idea behind developing this library was to create an easy, quick way to send JSON data to AWS services. JSON is an extremely common format and each AWS service has it's own API with different requirements for how to send data. `aws-json-dataset` will automatically handle batch calls when available and includes functionality to avoid exceeding service memory limits.

### Roadmap
- [ ] Support for Kinesis Data Streams
- [ ] Support for DynamoDB inserts, updates and deletes
- [ ] Support for S3, including gzip compression and JSON lines format
- [ ] Support for FIFO SQS queues ad SNS topics

## Quickstart
Install the library using pip.
```bash
pip install aws-json-dataset
```

Export the AWS region to the environment.
```bash
export AWS_REGION=<region>
```

Send JSON data to various AWS services.
```python
from awsjsondataset import AwsJsonDataset

# create a list of JSON objects
data = [ {"id": idx, "name": "<data>"} for idx in range(100) ]

# Wrap using AwsJsonDataset
dataset = AwsJsonDataset(data=data)

# Send to SQS queue
dataset.sqs("<sqs_queue_url>").send_messages()

# Send to SNS topic
dataset.sns("<sns_topic_arn>").publish_messages()

# Send to Kinesis Firehose stream
dataset.firehose("<delivery_stream_name>").put_records()
```

## Local Development
Follow the steps to set up the deployment environment.

### Prerequisites
* Python 3.10
* AWS credentials

### Creating a Python Virtual Environment
When developing locally, create a Python virtual environment to manage dependencies:
```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the project root.
```bash
AWS_REGION=<region>
```

***Important:*** *Always use a `.env` file or AWS SSM Parameter Store or Secrets Manager for sensitive variables like credentials and API keys. Never hard-code them, including when developing. AWS will quarantine an account if any credentials get accidentally exposed and this will cause problems.* &rarr; ***Make sure that `.env` is listed in `.gitignore`***

### AWS Credentials
Valid AWS credentials must be available to AWS CLI and SAM CLI. The easiest way to do this is running `aws configure`, or by adding them to `~/.aws/credentials` and exporting the `AWS_PROFILE` variable to the environment.

For more information visit the documentation page:
[Configuration and credential file settings](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)

## Unit Tests
Create a Python virtual environment to manage test dependencies.

```bash
python3 -m venv .venv-test
source .venv-test/bin/activate
pip install -U pip
pip install -r requirements-tests.txt
```
Run tests with the following command.
```bash
coverage run -m pytest
```

## Troubleshooting
* Check your AWS credentials in `~/.aws/credentials`
* Check that the environment variables are available to the services that need them
* Check that the correct environment or interpreter is being used for Python

<!-- ## References & Links -->

## Authors
**Primary Contact:** Gregory Lindsey (@abk7777)

## License
This library is licensed under the MIT-0 License. See the LICENSE file.