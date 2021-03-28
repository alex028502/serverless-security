import sys
import smtpd
import asyncore
import time

# thanks https://muffinresearch.co.uk/fake-smtp-server-with-python/

port = int(sys.argv[1])
folder = sys.argv[2]

print("HERE I AM")
print(sys.argv)


class FakeSMTPServer(smtpd.SMTPServer):
    def __init__(*args, **kwargs):
        print("listening on port %s and saving to %s" % (port, folder))
        smtpd.SMTPServer.__init__(*args, **kwargs)

    def process_message(*args, **kwargs):
        message_path = "%s/%s-%s.msg" % (folder, args[2], time.time())
        with open(message_path, "wb") as message_file:
            message_file.write(args[4])


smtp_server = FakeSMTPServer(("localhost", port), None)

try:
    asyncore.loop()
except KeyboardInterrupt:
    smtp_server.close()
