"""Use an in-process S3 emulator to rehearse versioned object recovery."""
import hashlib

import boto3
from moto import mock_aws


@mock_aws
def exercise():
    s3 = boto3.client("s3", region_name="us-east-1", aws_access_key_id="testing",
                      aws_secret_access_key="testing")
    bucket, key = "fictional-support-recovery", "handover.txt"
    s3.create_bucket(Bucket=bucket)
    s3.put_bucket_versioning(Bucket=bucket, VersioningConfiguration={"Status": "Enabled"})
    approved = b"Approved shift handover"
    first = s3.put_object(Bucket=bucket, Key=key, Body=approved)["VersionId"]
    bad = s3.put_object(Bucket=bucket, Key=key, Body=b"Incomplete handover")["VersionId"]
    def digest(version=None):
        args = {"VersionId": version} if version else {}
        data = s3.get_object(Bucket=bucket, Key=key, **args)["Body"].read()
        return hashlib.sha256(data).hexdigest()

    expected = hashlib.sha256(approved).hexdigest()
    assert digest(bad) != expected
    assert digest() != expected
    copy = s3.copy_object(Bucket=bucket, Key=key,
                          CopySource={"Bucket": bucket, "Key": key, "VersionId": first})
    assert copy["VersionId"] not in (first, bad)
    assert digest() == expected
    versions = s3.list_object_versions(Bucket=bucket, Prefix=key)["Versions"]
    assert len(versions) == 3 and digest(bad) != expected
    print("PASS | Local S3 emulator | 3 retained versions | restored SHA-256:", expected)


if __name__ == "__main__":
    exercise()
