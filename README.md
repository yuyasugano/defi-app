# Defi Application with AWS SAM

An application retrieves information from API and post it on Twitter. It's written in Python3.7 and deployed with `AWS SAM`. The service is currently working on https://twitter.com/BotDefi
 
## sam version

Ensure your `sam` version is as follows (some modifications would be required if you run other `sam` versions):
```sh
$ pip install aws-sam-cli
$ sam --version
SAM CLI, version 0.48.0
```
To install `aws-sam-cli`, visit https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html
 
## environment variables
 
vars.json
```
{
  "DefiApplication": {
    "API_KEY": "<DefiPulse API KEY>",
    "TWITTER_CONSUMER_KEY": "<Twitter Consumer Key>",
    "TWITTER_CONSUMER_SECRET": "<Twitter Consumer Secret>",
    "TWITTER_ACCESS_TOKEN": "<Twitter Access Token>",
    "TWITTER_ACCESS_SECRET": "<Twitter Access Secret>"
  }
} 
```
 
## setup steps
 
1. Prepare S3 bucket to upload the code and generate a compiled version of the template `compiled.yml`. You need to manually create an S3 bucket or use an existing one to store the code.
2. Install the external libraries for new Lambda function. The libraries need to be in the same directory and S3 location.
2. Compile `template.yml` and generate a compiled version of the template `compiled.yml` with `sam package`command
3. Submit the compiled template to CloudFormation and deploy your serverless application with `sam deploy`command as follows
```sh
cd lambda_function/
aws s3 mb s3://<Your S3 bucket> --region <Your region>
sam validate -t lambda_function/template.yml
sam package --template-file template.yml --s3-bucket <Your S3 bucket> --output-template-file compiled.yml
sam deploy --template-file compiled.yml --stack-name <Your stack name> --capabilities CAPABILITY_IAM --parameter-overrides ApiKey=<API_KEY> TwitterConsumerKey=<TWITTER_CONSUMER_KEY> TwitterConsumerSecret=<TWITTER_CONSUMER_SECRET> TwitterAccessToken=<TWITTER_ACCESS_TOKEN> TwitterAccessSecret=<TWITTER_ACCESS_SECRET>
```
 
## local test
```sh
sam local invoke DefiApplication --event event.json --region ap-northeast-1 --env-vars vars.json
```
 
## License

This library is licensed under the MIT License.
