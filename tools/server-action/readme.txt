
this is for running service restart commands on the device after deploying
ansible is only used for stuff that we can test locally
restarting the service is done with commands in the makefile
but this was repeated, so extracted and unit tested

this test here that mocks ssh is not as good as really testing it would be
like.. by setting up an ssh endpoint

