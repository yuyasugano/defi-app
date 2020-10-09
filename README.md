## DynamoDB time-series data pattern with AWS SAM

This example show how to set up DynamoDB time-series data for storing high frequent crypto currency board information with `AWS SAM`. 

## sam version

Ensure your `sam` version is as follows (some modifications would be required if you run other `sam` versions):
```sh
$ pip install aws-sam-cli
$ sam --version
SAM CLI, version 0.48.0
```
To install `aws-sam-cli`, visit https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html
 
## environment variables
 
Environment:
  Variables:
    API_KEY: !Ref ApiKey
    TWITTER_CONSUMER_KEY: !Ref TwitterConsumerKey
    TWITTER_CONSUMER_SECRET: !Ref TwitterSecret
    TWITTER_ACCESS_TOKEN: !Ref TwitterToken
    TWITTER_ACCESS_SECRET: !Ref TwitterSecret
 
## Setup steps

From `dynamodb-sam` folder:
1. Prepare S3 bucket to upload the code and generate a compiled version of the template `compiled.yml`. You need to manually create an S3 bucket or use an existing one to store the code.
2. Compile `template.yml` and generate a compiled version of the template `compiled.yml` with `sam package`command
3. Submit the compiled template to CloudFormation and deploy your serverless application with `sam deploy`command as follows
```sh
cd dynamodb-sam/
aws s3 mb s3://<Your S3 bucket>
sam package --template-file template.yml --s3-bucket <Your S3 bucket> --output-template-file compiled.yml
sam deploy --template-file compiled.yml --stack-name <Your stack name> --capabilities CAPABILITY_IAM --parameter-overrides TablePrefix=<Your prefix>
```

From `lambda-sam` folder:
1. Prepare S3 bucket to upload the code and generate a compiled version of the template `compiled.yml`. You need to manually create an S3 bucket or use an existing one to store the code.
2. Install the external libraries for new Lambda function. The libraries need to be in the same directory and S3 location.
2. Compile `template.yml` and generate a compiled version of the template `compiled.yml` with `sam package`command
3. Submit the compiled template to CloudFormation and deploy your serverless application with `sam deploy`command as follows
```sh
cd lambda_function/
sam package --template-file template.yml --s3-bucket <Your S3 bucket> --output-template-file compiled.yml
sam deploy --template-file compiled.yml --stack-name <Your stack name> --capabilities CAPABILITY_IAM --parameter-overrides ApiKey=<API_KEY> TwitterConsumerKey=<TWITTER_CONSUMER_KEY> TwitterConsumerSecret=<TWITTER_CONSUMER_SECRET> TwitterAccessToken=<TWITTER_ACCESS_TOKEN> TwitterAccessSecret=<TWITTER_ACCESS_SECRET>
```

## License

This library is licensed under the MIT License.
