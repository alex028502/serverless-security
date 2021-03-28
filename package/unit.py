# this module contains bits of code that I have failed to completely test in
# any meaningful way, so get tested partially with 'unit tests'.  If I change
# something in here, I probably need to try out the whole program instead of
# just running the tests before I know it works


def starttls(session, username, password):
    if not username and not password:
        return
    session.starttls()
    session.login(username, password)


def conditional_message(cond, message):
    if cond:
        print(message)
