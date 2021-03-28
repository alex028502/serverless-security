require 'json'

ignore_file = File.read('./bashcov-ignore.json')

ignore_list = JSON.parse(ignore_file)

# ignore_list = [".git", "venv", "gems", "node_modules", "coverage", ".target"]

SimpleCov.add_filter ignore_list

SimpleCov.command_name 'test:serverless-security'

SimpleCov.coverage_dir './coverage/sh'
