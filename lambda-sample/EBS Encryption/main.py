import boto3
from botocore.config import Config

import argparse
from time import time, sleep


def logger(func):
    def log(*args, **kwargs):
        start = time()
        print(f"start {func.__name__}...")
        result = func(*args, **kwargs)
        print(f"Done! Took {round(time() - start, 2)} sec")
        return result

    return log


@logger
def main():
    instance_id = parse_arg()
    ec2 = boto3.resource("ec2")

    instance = get_instance(ec2, instance_id)
    volume = get_volume_from_instance(instance)
    snapshot = create_snapshot(volume)

    encrypted_snapshot = copy_and_encrypt_snapshot(ec2, snapshot)
    encrypted_volume = create_volume_with_snapshot(
        ec2, encrypted_snapshot, instance.placement["AvailabilityZone"]
    )

    stopped = stop_instance(instance)

    detach_volume_from_instance(instance, volume)
    attach_volume_to_instance(instance, encrypted_volume)

    start_instance(instance)


# Get instance id from args
@logger
def parse_arg():
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--instance-id")
    args = args_parser.parse_args()
    instance_id = args.instance_id

    return instance_id


# Get instance by id
@logger
def get_instance(ec2, instance_id):
    return ec2.Instance(instance_id)


# Get root volume
@logger
def get_volume_from_instance(instance):
    return list(instance.volumes.all())[0]


# Create snapshot
@logger
def create_snapshot(volume):
    snapshot = volume.create_snapshot()
    snapshot.wait_until_completed()

    return snapshot


# Copy snapshot & encrypt
@logger
def copy_and_encrypt_snapshot(ec2, snapshot):
    copied_snapshot = snapshot.copy(
        Encrypted=True, KmsKeyId="alias/aws/ebs", SourceRegion="ap-northeast-2"
    )
    new_snapshot = ec2.Snapshot(copied_snapshot["SnapshotId"])
    new_snapshot.wait_until_completed()

    return new_snapshot


# Create volume
@logger
def create_volume_with_snapshot(ec2, snapshot, availability_zone):
    volume = ec2.create_volume(
        AvailabilityZone="ap-northeast-2a", SnapshotId=snapshot.id
    )

    return volume


# Stop Instance
@logger
def stop_instance(instance):
    instance.stop()
    instance.wait_until_stopped()

    return instance


# Detach volume from instance
@logger
def detach_volume_from_instance(instance, volume):
    instance.detach_volume(VolumeId=volume.id)

    while volume.state == "in-use":
        sleep(3)
        volume.reload()

    volume.delete()

    return instance


# Attach volume to instance
@logger
def attach_volume_to_instance(instance, volume):
    instance.attach_volume(Device="/dev/xvda", VolumeId=volume.id)

    return instance


# Start Instance
@logger
def start_instance(instance):
    instance.start()
    instance.wait_until_running()

    return instance


if __name__ == "__main__":
    main()