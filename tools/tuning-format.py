import sys

# the variable we tune the camera sensitivity with should look like 2:2:2.0
# no rules here about ints vs floats

# we could use asserts here except we want to be sure we tested everything

if len(sys.argv) != 2:
    raise Exception("wrong number of arguments %s" % sys.argv[1:])

tuning_string = sys.argv[1]

tuning_vars = tuning_string.split(":")

if len(tuning_vars) != 3:
    raise Exception("wrong number of vars %s" % tuning_string)

try:
    for x in tuning_vars:
        float(x)  # will throw an exception if it is not a number
except ValueError:
    raise Exception("%s - all values must be numbers" % tuning_string)

# one more line - test coverage experiment really
assert ":".join(tuning_vars) == tuning_string
