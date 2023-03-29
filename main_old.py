import uuid
import boto3
from botocore.exceptions import ClientError


def create_bucket_name(bucket_prefix):
    """Generate random name for s3 bucket using UID4’s string.
    :param bucket_prefix: prefix for bucket name to create
    The generated bucket name must be between 3 and 63 chars long
    """
    random_name = ''.join([bucket_prefix, str(uuid.uuid4())])
    if 3 < len(random_name) <= 63:
        return random_name
    else:
        raise "Random name must be between 3 and 63 chars long"


def create_bucket(bucket_prefix, s3_connection):
    """Create an S3 bucket in a specified region from the session object.
    :param bucket_prefix: prefix for bucket name to create
    :param s3_connection: s3 connection type
    """
    session = boto3.session.Session()
    current_region = session.region_name
    bucket_name = create_bucket_name(bucket_prefix)
    bucket_response = s3_connection.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': current_region})
    print(bucket_name, current_region)
    return bucket_name, bucket_response


def create_temp_file(size, file_name, file_content):
    """Randomize the file name using UID4’s string.
    :param size: integer for file size
    :param file_name: file name
    :param file_content: file's content
    """
    if type(size) == int:
        random_file_name = ''.join([str(uuid.uuid4().hex[:6]), file_name])
        with open(random_file_name, 'w') as f:
            f.write(str(file_content) * int(size))
        return random_file_name
    else:
        raise ("Size is Not an Integer")


def copy_to_bucket(bucket_from_name, bucket_to_name, file_name):
    """ copy files from one bucket to another on the same region.
    :param bucket_from_name: source bucket
    :param bucket_to_name: destination bucket
    :param file_name: file name
    """
    try:
        copy_source = {
            'Bucket': bucket_from_name,
            'Key': file_name
        }
        s3_resource.Object(bucket_to_name, file_name).copy(copy_source)
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("Bucket or File Not Found")
        if e.response['Error']['Code'] == "NoSuchBucket":
            print("NoSuchBucket")
        else:
            print("Unexpected error: %s" % e)


def enable_bucket_versioning(bucket_name):
    "Enable versioning for a Specific bucket"
    try:
        bkt_versioning = s3_resource.BucketVersioning(bucket_name)
        bkt_versioning.enable()
        print(bkt_versioning.status)
    except ClientError as e:
        print(e.response['Error']['Code'])
        if e.response['Error']['Code'] == "NoSuchBucket":
            print("NoSuchBucket")
        else:
            print("Unexpected error: %s" % e)

def delete_all_objects(bucket_name):
    "Delete every single object within the bucket"
    try:
        res = []
        bucket=s3_resource.Bucket(bucket_name)
        for obj_version in bucket.object_versions.all():
            res.append({'Key': obj_version.object_key,'VersionId': obj_version.id})
        print(res)
        bucket.delete_objects(Delete={'Objects': res})
    except ClientError as e:
        print(e.response['Error']['Code'])
        if e.response['Error']['Code'] == "NoSuchBucket":
            print("NoSuchBucket")
        else:
            print("Unexpected error: %s" % e)


if __name__ == "__main__":
    s3_resource = boto3.resource('s3')

    # Creating First Bucket - using the client
    first_bucket_name, first_response = create_bucket(bucket_prefix='firstpythonbucket', s3_connection=s3_resource.meta.client)
    print(first_response)

    # Creating Second Bucket - using the resource
    second_bucket_name, second_response = create_bucket(bucket_prefix='secondpythonbucket', s3_connection=s3_resource)
    print(second_response)

   #  Create First File
    first_file_name = create_temp_file(300, 'firstfile.txt', 'f')

    # Creating Bucket and Object Instances
    first_bucket = s3_resource.Bucket(name=first_bucket_name)
    first_object = s3_resource.Object(
        bucket_name=first_bucket_name, key=first_file_name)

    # Understanding Sub-resources
    first_object_again = first_bucket.Object(first_file_name)
    first_bucket_again = first_object.Bucket()

    # Uploading a File - using an Object instance
    s3_resource.Object(first_bucket_name, first_file_name).upload_file(
        Filename=first_file_name)

    # # Downloading a File - using an Object instance
    s3_resource.Object(first_bucket_name, first_file_name).download_file(
        f'/tmp/{first_file_name}')  # Python 3.6+

    # Copying an Object Between Buckets
    copy_to_bucket(first_bucket_name, second_bucket_name, first_file_name)

    # Deleting an Object From the Second bucket
    s3_resource.Object(second_bucket_name, first_file_name).delete()

    # Create a File on a bucket and provide it with public-read permissions
    second_file_name = create_temp_file(400, 'secondfile.txt', 's')
    second_object = s3_resource.Object(first_bucket.name, second_file_name)
    second_object.upload_file(second_file_name, ExtraArgs={'ACL': 'public-read'})

    # Get the ObjectAcl instance from the Object
    second_object_acl = second_object.Acl()
    print(second_object_acl.grants)

    # Make Project Private
    response = second_object_acl.put(ACL='private')
    print(second_object_acl.grants)

    # server-side encryption using the AES-256 algorithm where AWS manages both the encryption and the keys
    third_file_name = create_temp_file(300, 'thirdfile.txt', 't')
    third_object = s3_resource.Object(first_bucket_name, third_file_name)
    third_object.upload_file(third_file_name, ExtraArgs={'ServerSideEncryption': 'AES256'})
    print(third_object.server_side_encryption)

   # Change the Storage Class of an Existing Object
    third_object.upload_file(third_file_name, ExtraArgs={'ServerSideEncryption': 'AES256', 'StorageClass': 'STANDARD_IA'})

    # Reload the object, and you can see its new storage class
    third_object.reload()
    print(third_object.storage_class)

    # Enable versioning for the first bucket
    enable_bucket_versioning(first_bucket_name)

    # create two new versions for the first file Object, one with the contents of the original file and one with the contents of the third file
    s3_resource.Object(first_bucket_name, first_file_name).upload_file(first_file_name)
    s3_resource.Object(first_bucket_name, first_file_name).upload_file(third_file_name)

    # Reupload the second file, which will create a new version
    s3_resource.Object(first_bucket_name, second_file_name).upload_file(second_file_name)

    # Retrieve the Latest Available Version of your Objects
    print(s3_resource.Object(first_bucket_name, first_file_name).version_id)

    # traverse all the buckets in the account - using resource’s buckets attribute
    for bucket in s3_resource.buckets.all():
        print(bucket.name)

    # List all the Objects From a Bucket
    for obj in first_bucket.objects.all():
        print(obj.key)

    # List all the Objects From a Bucke - using Object
    for obj in first_bucket.objects.all():
        subsrc = obj.Object()
        print(obj.key, obj.storage_class, obj.last_modified,subsrc.version_id, subsrc.metadata)

    # Deleting a Non-empty Bucket
    delete_all_objects(first_bucket_name)

    # Deleting a Bucket which doesn’t have versioning enabled
    s3_resource.Object(second_bucket_name, first_file_name).upload_file(first_file_name)
    delete_all_objects(second_bucket_name)

    # Deleting first Bucket
    s3_resource.Bucket(first_bucket_name).delete()
    # Deleting second Bucket - using client
    s3_resource.meta.client.delete_bucket(Bucket=second_bucket_name)

