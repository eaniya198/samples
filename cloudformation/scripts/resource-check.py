from colorama import Fore, Style
from pprint import pprint
from copy import deepcopy
from datetime import timezone, datetime

import boto3

current_region = boto3.Session()
global_region = boto3.Session(region_name="us-east-1")

ec2 = current_region.client("ec2")
elb = current_region.client("elbv2")
s3 = current_region.client("s3")
cloudfront = global_region.client("cloudfront")


class LEVEL:
    INFO = 0
    WARN = 1
    CRITICAL = 2


def get_vpc_and_subnets():
    vpcs = ec2.describe_vpcs(Filters=[{"Name": "is-default", "Values": ["false"]}])[
        "Vpcs"
    ]

    vpc_ids_with_flow_log = [
        flow_log["ResourceId"] for flow_log in ec2.describe_flow_logs()["FlowLogs"]
    ]
    subnets = ec2.describe_subnets()["Subnets"]
    endpoints = ec2.describe_vpc_endpoints()["VpcEndpoints"]

    vpc_reports = []
    for vpc in vpcs:
        vpc_name = [tag["Value"] for tag in vpc.get("Tags", []) if tag["Key"] == "Name"]
        vpc_flow_log = True if vpc["VpcId"] in vpc_ids_with_flow_log else False
        vpc_endpoint_names = [
            endpoint["ServiceName"]
            for endpoint in endpoints
            if endpoint["VpcId"] == vpc["VpcId"]
        ] or []

        vpc_subnets = [subnet for subnet in subnets if subnet["VpcId"] == vpc["VpcId"]]

        subnet_reports = []
        for subnet in vpc_subnets:
            subnet_name = [
                tag["Value"] for tag in subnet.get("Tags", []) if tag["Key"] == "Name"
            ]

            subnet_reports.append(
                {
                    "type": "subnet",
                    "name": subnet_name[0] if subnet_name else subnet["SubnetId"],
                    "cidr": subnet["CidrBlock"],
                    "az": subnet["AvailabilityZone"],
                }
            )

        vpc_reports.append(
            {
                "type": "vpc",
                "name": vpc_name[0] if vpc_name else vpc["VpcId"],
                "cidr": vpc["CidrBlock"],
                "flow_log": vpc_flow_log,
                "endpoints": ", ".join(vpc_endpoint_names) or None,
                "subnets": subnet_reports,
            }
        )

    result = vpc_reports
    return result


def get_security_groups():
    security_groups = ec2.describe_security_groups()["SecurityGroups"]
    security_groups = [sg for sg in security_groups if sg["GroupName"] != "default"]

    security_group_reports = []
    for sg in security_groups:
        rule_reports = []
        for is_egress, rules in enumerate(
            [sg["IpPermissions"], sg["IpPermissionsEgress"]]
        ):
            for rule in rules:
                if rule["IpProtocol"] == "-1":
                    port_range = "-1"
                else:
                    port_range = (
                        rule["ToPort"]
                        if rule["FromPort"] == rule["ToPort"]
                        else f"{rule['FromPort']}-{rule['ToPort']}"
                    )
                arrow = "->" if is_egress else "<-"
                for ipv4 in rule["IpRanges"]:
                    rule_reports.append(
                        {
                            f"{arrow}": f"{rule['IpProtocol']} {port_range} \t{arrow} {ipv4['CidrIp']}  \t{ipv4.get('Description', '')}"
                        }
                    )
                for ipv6 in rule["Ipv6Ranges"]:
                    rule_reports.append(
                        {
                            f"{arrow}": f"{rule['IpProtocol']} {port_range} \t{arrow} {ipv6['CidrIpv6']}  \t{ipv6.get('Description', '')}"
                        }
                    )
                for prefix_list in rule["PrefixListIds"]:
                    rule_reports.append(
                        {
                            f"{arrow}": f"{rule['IpProtocol']} {port_range} \t{arrow} {prefix_list['PrefixListId']}  \t{prefix_list.get('Description', '')}"
                        }
                    )
                for group in rule["UserIdGroupPairs"]:
                    group_name = [
                        g["GroupName"]
                        for g in security_groups
                        if g["GroupId"] == group["GroupId"]
                    ]
                    rule_reports.append(
                        {
                            f"{arrow}": f"{rule['IpProtocol']} {port_range} \t{arrow} {group_name[0] if group_name else group['GroupId']}  \t{group.get('Description', '')}"
                        }
                    )
        security_group_reports.append(
            {"type": "sg", "name": sg["GroupName"], "rules": rule_reports}
        )
        # sg["IpPermissions"][0]["UserIdGroupPairs"]
    result = security_group_reports
    return result


def get_instances():
    instances = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )["Reservations"]

    instance_reports = []
    for instance in instances:
        instance = instance["Instances"][0]

        instance_name = [
            tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"
        ]
        instance_type = instance["InstanceType"]
        az = instance["Placement"]["AvailabilityZone"]
        security_groups = ", ".join(
            [
                ", ".join([group["GroupName"] for group in eni["Groups"]])
                for eni in instance["NetworkInterfaces"]
            ]
        )
        instance_profile = instance["IamInstanceProfile"]["Arn"]
        monitoring = instance["Monitoring"]["State"] == "enabled"
        uptime = datetime.now(timezone.utc) - instance["LaunchTime"]
        uptime_string = f"{uptime.seconds // 3600}h {uptime.seconds // 60 % 60}m ago"

        instance_reports.append(
            {
                "type": "instance",
                "name": instance_name[0] if instance_name else instance["InstanceId"],
                "instance_type": instance_type,
                "security_group": security_groups,
                "instance_profile": instance_profile,
                "az": az,
                "monitoring": monitoring,
                "uptime": uptime_string,
            }
        )
    result = instance_reports
    return result


def get_cloudfront():
    distributions = cloudfront.list_distributions()["DistributionList"]["Items"]

    distribution_reports = []
    for distribution in distributions:
        config = cloudfront.get_distribution_config(Id=distribution["Id"])[
            "DistributionConfig"
        ]
        logging_path = (
            config["Logging"]["Bucket"] + "/" + config["Logging"]["Prefix"]
            if config["Logging"]["Enabled"]
            else None
        )
        distribution_reports.append(
            {
                "type": "cloudfront",
                "name": distribution["DomainName"],
                "log_bucket": logging_path,
            }
        )
    result = distribution_reports
    return result


def get_target_groups():
    target_groups = elb.describe_target_groups()["TargetGroups"]

    target_group_reports = []
    for tg in target_groups:
        targets = elb.describe_target_health(TargetGroupArn=tg["TargetGroupArn"])[
            "TargetHealthDescriptions"
        ]

        target_reports = [
            {
                "type": "target",
                "name": target["Target"]["Id"],
                "state": target["TargetHealth"]["State"],
                "az": target["Target"]["AvailabilityZone"],
            }
            for target in targets
        ]

        target_group_reports.append(
            {
                "type": "target group",
                "name": tg["TargetGroupName"],
                "targets": target_reports,
            }
        )

    result = target_group_reports
    return result


def get_buckets():
    buckets = s3.list_buckets()["Buckets"]

    bucket_reports = []
    for bucket in buckets:
        bucket_versioning = (
            s3.get_bucket_versioning(Bucket=bucket["Name"]).get("Status") == "Enabled"
        )
        bucket_logging = bool(
            s3.get_bucket_logging(Bucket=bucket["Name"]).get("LoggingEnabled")
        )
        default_encryption = [
            rule
            for rule in s3.get_bucket_encryption(Bucket=bucket["Name"])[
                "ServerSideEncryptionConfiguration"
            ]["Rules"]
            if rule.get("ApplyServerSideEncryptionByDefault")
        ][0]
        sse_algorithm = default_encryption["ApplyServerSideEncryptionByDefault"][
            "SSEAlgorithm"
        ]
        bucket_reports.append(
            {
                "type": "s3",
                "name": bucket["Name"],
                "versioning": bucket_versioning,
                "logging": bucket_logging,
                "bucket_key": default_encryption["BucketKeyEnabled"],
                "encryption_key": sse_algorithm,
            }
        )
    result = bucket_reports
    return result


def pprint_resources(resources: list[dict], depth=0):
    adjust = 1
    for resource in resources:
        # If all values of resource are empty, skip it
        for key, value in resource.items():
            if key in ["type", "name"]:
                continue
            if value not in [[]]:
                break
        else:
            continue
        # print head
        try:
            print(
                "\t" * depth
                + f"{Fore.GREEN}{Style.BRIGHT}=== {resource['type'].upper()}: {resource['name']} ==={Fore.RESET}{Style.RESET_ALL} "
            )
        except KeyError:
            adjust = 0
            pass

        # print body
        for key, value in resource.items():
            if key in ["type", "name"]:
                continue
            if type(value) == list:
                pprint_resources(value, depth=depth + 1)
                continue
            print(
                "\t" * (depth + adjust)
                + f"{Fore.BLACK}{key}: {Fore.WHITE}{value}{Fore.RESET}"
            )
    if depth == 0:
        print(end="\n\n")
    return


def check_buckets(resources: list[dict], level=LEVEL.WARN):
    resources = deepcopy(resources)

    for resource in resources:
        if resource["versioning"]:
            del resource["versioning"]
        if resource["bucket_key"]:
            del resource["bucket_key"]
        if resource["logging"] or LEVEL.WARN < level:
            del resource["logging"]
        if resource["encryption_key"] == "aws:kms" or LEVEL.WARN < level:
            del resource["encryption_key"]
    return resources


def check_security_groups(resources: list[dict], level=LEVEL.WARN):
    resources = deepcopy(resources)
    for resource in resources:
        for rule_definition in resource["rules"][:]:
            rule = list(rule_definition.values())[0].split()

            protocol, port_range, arrow, target, description = *rule[:4], " ".join(
                rule[4:]
            )

            # Pass if rule specify tcp port, target, description.
            if (
                protocol == "tcp"
                and port_range.count("-") == 0
                and target not in ["0.0.0.0/0", "::/0"]
                and description
            ):
                resource["rules"].remove(rule_definition)
            # Pass if egress rule is for 80, 443 outbuond any open
            elif (
                protocol == "tcp"
                and port_range in ["80", "443"]
                and arrow == "->"
                and target in ["0.0.0.0/0", "::/0"]
                and description
            ):
                resource["rules"].remove(rule_definition)
            # Alert empty description on non-CRITICAL level
            elif description and LEVEL.WARN < level:
                resource["rules"].remove(rule_definition)
    return resources


def check_target_groups(resources: list[dict], level=LEVEL.WARN):
    resources = deepcopy(resources)

    reports = []
    for resource in resources:
        unhealthy_targets = []
        az_count = {}
        for target in resource["targets"]:
            if target["state"] != "healthy":
                unhealthy_targets.append(target)
                continue
            try:
                az_count[target["az"]] += 1
            except KeyError:
                az_count[target["az"]] = 1
        reports.append(
            {
                "type": resource["type"],
                "name": resource["name"],
                "az_counts": ", ".join(
                    [f"{az}: {count}" for az, count in az_count.items()]
                )
                or None,
                "unhealthy_targets": unhealthy_targets,
            }
        )
    return reports


def check_vpcs(resources: list[dict], level=LEVEL.WARN):
    resources = deepcopy(resources)

    for vpc in resources:
        if vpc["endpoints"]:
            del vpc["endpoints"]
        if vpc["flow_log"] or LEVEL.WARN < level:
            del vpc["flow_log"]
        if LEVEL.INFO < level:
            del vpc["cidr"]
            del vpc["subnets"]
    return resources


def check_instances(resources: list[dict], level=LEVEL.WARN):
    resources = deepcopy(resources)

    az_count = {}
    for instance in resources:
        try:
            az_count[instance["az"]] += 1
        except KeyError:
            az_count[instance["az"]] = 1

        hour, minute, _ = [token[:-1] for token in instance["uptime"].split()]
        if int(hour) or int(minute) > 20 or LEVEL.WARN < level:
            del instance["uptime"]
        if instance["monitoring"] or LEVEL.WARN < level:
            del instance["monitoring"]
        if len(instance["security_group"].split(",")) == 1 or LEVEL.WARN < level:
            del instance["security_group"]
        if LEVEL.INFO < level:
            del instance["az"]
    az_count["type"] = "report"
    az_count["name"] = "az_count"
    resources.append(az_count)
    return resources


if __name__ == "__main__":
    ##
    ## Check deployment state
    ##
    # Check targets if they are healthy and evenly distributed
    target_groups = get_target_groups()
    pprint_resources(check_target_groups(target_groups))

    # Check instance uptime and security settings
    instances = get_instances()
    pprint_resources(check_instances(instances, level=LEVEL.WARN))

    ##
    ## Check security configurations
    ##
    # Check flow logs and endpoints
    vpcs = get_vpc_and_subnets()
    pprint_resources(check_vpcs(vpcs, level=LEVEL.WARN))

    # Check security group rules if they have descriptions and strict rules
    security_groups = get_security_groups()
    pprint_resources(check_security_groups(security_groups, level=LEVEL.WARN))

    # Check bucket configurations
    buckets = get_buckets()
    buckets = [
        bucket
        for bucket in buckets
        if not bucket["name"].startswith("aws")
        and not bucket["name"].startswith("cf-templates")
    ]
    pprint_resources(check_buckets(buckets, level=LEVEL.WARN))

    ##
    ## Check logging configurations
    ##
    distributions = get_cloudfront()
    pprint_resources(distributions)
