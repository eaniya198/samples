import json
import os
import sys

DELETE_KEYS = ["taskDefinitionArn", "revision", "status", "requiresAttributes", "registeredAt", "registeredBy"]
TEMPLATE_VAR = "<IMAGE1_NAME>"

def check_file_exists(path: str) -> bool:
    return os.path.exists(path)

def get_arguments():
    return sys.argv[1:]

def parse_taskdef(path):
    with open(path, "r") as f:
        taskdef: dict = json.loads(f.read())

    for key in DELETE_KEYS:
        taskdef.pop(key, None)
    
    if taskdef.get("tags", None) == []:
        taskdef.pop("tags")

    taskdef["containerDefinitions"][0]["image"] = TEMPLATE_VAR

    with open(path, "w") as f:
        taskdef = f.write(json.dumps(taskdef, indent=4))

if __name__ == "__main__":
    args = get_arguments()

    if len(args) == 0:
        print("Provide taskdef filename to parse")
        sys.exit(1)

    for filename in args:
        if check_file_exists(filename):
            parse_taskdef(filename)
        print(f"{filename} edited")
