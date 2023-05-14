from typing import TypedDict, Iterable, Reversible
from threading import Thread
from time import sleep
from sys import exit
from sys import stdout as STDOUT

import logging

try:
    import boto3
    from colorama import Fore, Style
except ImportError:
    print(f"boto3 or colorama is not installed for your interpreter.")
    exit(1)


logger = logging.getLogger()
logging.basicConfig(stream=STDOUT)
logger.setLevel(logging.INFO)

REGION = "ap-northeast-2"
client = boto3.client("cloudformation", region_name=REGION)


def get_template_body(path: str) -> str:
    with open(path, "r") as f:
        body = f.read()
    return body


def create_stack(stack: dict) -> TypedDict:
    response = client.create_stack(
        StackName=stack["StackName"],
        TemplateBody=stack["TemplateBody"],
        Parameters=stack["Parameters"],
        Capabilities=stack["Capabilities"],
    )
    return response


def update_stack(stack: dict) -> TypedDict:
    response = client.update_stack(
        StackName=stack["StackName"],
        TemplateBody=stack["TemplateBody"],
        Parameters=stack["Parameters"],
        Capabilities=stack["Capabilities"],
    )
    return response


def delete_stack(stack_name) -> None:
    client.delete_stack(StackName=stack_name)
    return None


def get_template_summary(template_body):
    response = client.get_template_summary(TemplateBody=template_body)
    return response


def wait_stack(operation, stack_name, delay=5, max_attempts=120):
    waiter = client.get_waiter(operation)

    waiter.wait(
        StackName=stack_name, WaiterConfig={"Delay": delay, "MaxAttempts": max_attempts}
    )

    return True


def build_template(stack_name, template_path, user_parameters: dict):
    template_body = get_template_body(template_path)
    summary = get_template_summary(template_body)

    parameters = []
    for parameter in summary["Parameters"]:
        try:
            parameters.append(
                {
                    "ParameterKey": parameter["ParameterKey"],
                    "ParameterValue": user_parameters[parameter["ParameterKey"]],
                    "UsePreviousValue": False,
                }
            )
        except KeyError:
            parameters.append(
                {"ParameterKey": parameter["ParameterKey"], "UsePreviousValue": True}
            )

    stack = {
        "StackName": stack_name,
        "TemplateBody": template_body,
        "Parameters": parameters,
        "Capabilities": summary.get("Capabilities", []),
    }

    return stack


def deploy_in_order(stacks: Iterable[dict], method=create_stack):
    if method == create_stack:
        wait_operation = "stack_create_complete"
        message = "created"
    elif method == update_stack:
        wait_operation = "stack_update_complete"
        message = "updated"
    else:
        raise ValueError(method)

    try:
        for stack in stacks:
            response = method(stack)
            stack["StackId"] = response["StackId"]
            logger.info(f"{stack['StackName']} is being {message}")

            wait_stack(wait_operation, stack["StackName"])
            logger.info(f"{stack['StackName']} is {message}")
    except Exception as e:
        logger.error(e)

    return stacks


def deploy_parallel(stack_sequences: Iterable[Iterable[dict]], method=create_stack):
    jobs = []
    for stacks in stack_sequences:
        job = Thread(target=deploy_in_order, args=[stacks, method], daemon=True)
        job.start()

        jobs.append(job)

    while list(filter(lambda job: job.is_alive(), jobs)):
        sleep(1)

    return stack_sequences


def delete_in_reverse_order(stacks: Reversible[dict]):
    try:
        for param in reversed(stacks):
            delete_stack(param["StackName"])
            logger.info(f"{param['StackName']} is being deleted")

            wait_stack("stack_delete_complete", param["StackName"])
            param.pop("StackId", None)
            logger.info(f"{param['StackName']} is deleted")
    except Exception as e:
        logger.error(e)

    return stacks


def delete_parallel(stack_sequences: Iterable[Iterable[dict]]):
    jobs = []
    for stacks in stack_sequences:
        job = Thread(target=delete_in_reverse_order, args=[stacks], daemon=True)
        job.start()
        jobs.append(job)

    while list(filter(lambda job: job.is_alive(), jobs)):
        sleep(1)

    return stack_sequences


def describe_sequence(stack_sequences: Iterable[Iterable[dict]]):
    for num, stacks in enumerate(stack_sequences, start=1):
        print(f"{Fore.WHITE}===== Stack sequence {num} ====={Fore.RESET}")

        for stack in stacks:
            print(
                f"{Fore.LIGHTGREEN_EX}{Style.BRIGHT}{stack['StackName']}\t{stack['Capabilities']}{Fore.RESET}{Style.RESET_ALL}"
                if stack["Capabilities"]
                else f"{Fore.LIGHTGREEN_EX}{stack['StackName']}"
            )
            not_specified_params = []
            for param in stack["Parameters"]:
                if param["UsePreviousValue"]:
                    not_specified_params.append(param["ParameterKey"])
                else:
                    print(
                        f"\t{Fore.LIGHTBLACK_EX}{param['ParameterKey']}: {Fore.WHITE}{Style.BRIGHT}{param['ParameterValue']}{Fore.RESET}{Style.RESET_ALL}"
                    )
            if not_specified_params:
                print(
                    f"\t{Fore.LIGHTBLACK_EX}Use previous value: {', '.join(not_specified_params)}{Fore.RESET}"
                )

    return


def check_user_admission():
    retry = 0
    while retry < 2:
        admission = input("Coninue with those stacks? (y / N): ").lower()
        if admission == "n":
            break
        elif admission == "y":
            return
        else:
            print("Please enter 'y' or 'n'")
            retry += 1
    print("Cancelled")
    exit(0)


if __name__ == "__main__":
    TEMPLATE_DIRECTORY = "C:/skills/template/"

    apps = ["customer", "order", "product", "stress"]
    ARTIFACT_BUCKET = "wsi-hmoon-artifacts"
    CODECOMMIT_BRANCH = "main"

    codecommit_stack = (
        build_template(
            stack_name=f"dev-{app_name}-git",
            template_path=TEMPLATE_DIRECTORY + "blue-green/codecommit.yaml",
            user_parameters={"RepositoryName": f"dev-{app_name}"},
        )
        for app_name in apps
    )

    codebuild_stack = (
        build_template(
            stack_name=f"dev-{app_name}-build",
            template_path=TEMPLATE_DIRECTORY + "blue-green/codebuild.yaml",
            user_parameters={
                "CodeBuildProjectName": f"dev-{app_name}-build",
                "CodeCommitRepositoryName": f"dev-{app_name}",
                "CodeCommitBranchName": CODECOMMIT_BRANCH,
                "ArtifactBucketName": ARTIFACT_BUCKET,
                "ECRRepositoryName": app_name,
            },
        )
        for app_name in apps
    )

    codedeploy_stack = (
        build_template(
            stack_name=f"dev-{app_name}-deploy",
            template_path=TEMPLATE_DIRECTORY + "blue-green/codedeploy.yaml",
            user_parameters={
                "CodeDeployApplicationName": f"dev-{app_name}-deploy",
                "ECSServiceName": app_name,
                "TargetGroup1Name": f"{app_name}-1",
                "TargetGroup2Name": f"{app_name}-2",
            },
        )
        for app_name in apps
    )

    codepipeline_stack = (
        build_template(
            stack_name=f"{REGION}-{app_name}-pipeilne",
            template_path=TEMPLATE_DIRECTORY + "blue-green/codepipeline.yaml",
            user_parameters={
                "CodePipelineName": f"dev-{app_name}-pipeline",
                "CodeCommitRepositoryName": f"dev-{app_name}",
                "CodeCommitBranchName": CODECOMMIT_BRANCH,
                "CodeBuildProjectName": f"dev-{app_name}-build",
                "CodeDeployApplicationName": f"dev-{app_name}-deploy",
                "CodeDeployDeploymentGroupName": f"wsi-cluster-{app_name}",
                "ArtifactBucketName": ARTIFACT_BUCKET,
            },
        )
        for app_name in apps
    )

    vpc_stack = (
        build_template(
            stack_name=f"vpc",
            template_path=TEMPLATE_DIRECTORY + "vpc_data_subnet.yaml",
            user_parameters={"NamePrefix": "wsi"},
        )
        for _ in range(1)
    )

    try:
        ### Defining stacks as generator is recommended for lazy evaluation.
        ### If you want to reference stacks later, convert to list here.
        # codepipeline_stack = list(codepipeline_stack)

        sequences = list(
            zip(
                # codecommit_stack,
                # codebuild_stack,
                # codedeploy_stack,
                # codepipeline_stack,
                vpc_stack,
            )
        )

        ### Describe stacks before deployment
        describe_sequence(sequences)
        check_user_admission()

        ### Execute
        delete_parallel(sequences)
        # deploy_parallel(sequences, method=update_stack)
    except Exception as e:
        logger.error(e)
