import sys
import configparser

config = configparser.ConfigParser()

config.read(sys.argv[1])

print(config[sys.argv[2]][sys.argv[3]])
