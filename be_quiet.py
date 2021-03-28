from package import unit

# don't remember why I used to need this - I think the path
# used to be more complicated
# spec = importlib.util.spec_from_file_location(
#     "package",
#     "./package/__init__.py",
# )
# module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(module)
# sys.modules[spec.name] = module
# spec.loader.exec_module(module)

# this is really a test - we only test the quiet case since the verbose case is
# already covered by the rest tests... and we don't actually check the result
# of the verbose case because it's just for debugging - we just need to pretty
# sure that this is silent when it should be - or we are just meeting our test
# coverage goals - one or the other
# the assertion is done in the script that calls this

unit.conditional_message(False, "NOBODY WILL EVER SEE THIS")
