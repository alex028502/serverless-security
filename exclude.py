import yaml

with open("./playbooks/core.yml", "r") as stream:
    print(yaml.safe_load(stream)[0]["tasks"])
