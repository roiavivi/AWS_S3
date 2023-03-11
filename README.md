Amazon Web Services (AWS) has become a leader in cloud computing. 

One of its core components is S3, the object storage service offered by AWS. 

With its impressive availability and durability, it has become the standard way to store videos, images, and data. 

You can combine S3 with other services to build infinitely scalable applications.

Boto3 is the name of the Python SDK for AWS. It allows you to directly create, update, and delete AWS resources from your Python scripts.

Using this repo you will be able to:
- Create S3 bucket on AWS 
- Create files on S3 bucket
- upload files to S3 bucket
- Download files from S3 bucket
- Change file's attributes
- Copy objects between buckets



How to Run the APP:

1. To set these variables on Linux, OS X, or Unix, use export:


    AWS_ACCESS_KEY_ID=your_access_key_id
    AWS_SECRET_ACCESS_KEY=your_secret_access_key
    AWS_DEFAULT_REGION=your_aws_default_region


2. Build & Run the Docker:


    docker build -t my_app .


    docker run -it --rm \
       -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID /\
       -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION /\
       -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY /\
       my_app


See also
* https://realpython.com/python-boto3-aws-s3/