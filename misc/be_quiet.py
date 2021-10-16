import importlib
import sys

unit_path = sys.argv[1]

unit_spec = importlib.util.spec_from_file_location(
    "unit",
    unit_path,
)
unit = importlib.util.module_from_spec(unit_spec)
unit_spec.loader.exec_module(unit)

# this is really a test - we only test the quiet case since the verbose case is
# already covered by the rest tests... and we don't actually check the result
# of the verbose case because it's just for debugging - we just need to pretty
# sure that this is silent when it should be - or we are just meeting our test
# coverage goals - one or the other
# the assertion is done in the script that calls this

unit.conditional_message(False, "NOBODY WILL EVER SEE THIS")
