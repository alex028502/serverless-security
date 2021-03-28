import os
import sys
import uuid
import smtplib
import time

# sends a one line phrase to our internal smtp server
# is used both to test smtp server, and since we have it anyway, to receive
# updates from the test process run by monitor.py

host = sys.argv[1]
port = int(sys.argv[2])
sender = sys.argv[3]
message = " ".join(sys.argv[4:]) + "\n"  # usually just one argument

print("sending the following message to %s:%s from %s" % (host, port, sender))
print(message)

session = smtplib.SMTP(host, port)
# no headers - will save what we send it
session.set_debuglevel(1)

to_address = str(uuid.uuid4())
# looks like smtpd can't check the recipient on the envelope so we can't use
# this to test that our envelope recipient and header recipient match - this
# proves we can put anything in there

session.sendmail(sender, [to_address], message)
session.quit()

try:
    time.sleep(float(os.environ["DELAY_AFTER_MAIL"]))
except KeyError:
    pass
