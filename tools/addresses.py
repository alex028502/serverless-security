# command line tool to get email addresses from
# settings file - so that we don't have to depend on jq

import sys
import json

settings_path = sys.argv[1]

# read file
with open(settings_path, "r") as settings_file:
    data = settings_file.read()

settings_data = json.loads(data)

print(settings_data["sender"])

for recipient in settings_data["recipients"]:
    print(recipient)
