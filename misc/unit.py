import importlib.util

# thanks! https://stackoverflow.com/a/50395128
# I hope one day I find out what all of this means!
spec = importlib.util.spec_from_file_location(
    "unit",
    "./package/unit.py",
)
sut = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sut)

# these tests are kind of contrived to cover stuff that's real tests can't
# cover.  If I have to change one of these tests to make a change, it is a sign
# that I probably have to manually test the whole system too

# since our pytest set-up doesn't test anything in process and runs
# twice against different environments, I took this out of pytest


class FakeSession:
    def __init__(self):
        self._starttls = False
        self.username = None
        self.password = None

    def starttls(self):
        self._starttls = True

    def login(self, username, password):
        self.username = username
        self.password = password


fake_session = FakeSession()
username = "dan"
password = "p@$$w0rd"
assert not fake_session.password
assert not fake_session.username
assert not fake_session._starttls
sut.starttls(fake_session, username, password)
assert fake_session.password == password
assert fake_session.username == username
assert fake_session._starttls
