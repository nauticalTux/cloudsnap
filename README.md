# cloudsnap

A Python and boto3 project to manage AWS EC2 instance snapshots.

## About

This project is a learning excersize in creating a python3 CLI.

## Configure

The `snapper.py` script requires an AWS User be set up within IAM (username: *cloudsnap*). The *cloudsnap* user must have the proper permissions assigned - I utilized the *AmazonEC2FullAccess* IAM policy.

The script also uses the AWS configuration file (\~/.aws/config) and the credential file (\~/.aws/credentials) provided by the awscli tool. Once awscli is installed, you can configure the *cloudsnap* user by executing the following command: 

    aws configure --profile cloudsnap





