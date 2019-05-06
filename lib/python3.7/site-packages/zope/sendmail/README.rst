=====================
 Using zope.sendmail
=====================

This package is useful when your Zope 3 application wants to send email.  It
integrates with the transaction mechanism and queues your emails to be sent on
successful commits only.


API
===

An application that wants to send an email can do so by getting the appropriate
:class:`zope.sendmail.interfaces.IMailDelivery` utility.  The standard library's email module is useful for
formatting the message according to RFC-2822::

    import email.MIMEText
    import email.Header
    from zope.sendmail.interfaces import IMailDelivery
    from zope.component import getUtility

    def send_email(sender, recipient, subject, body):
        msg = email.MIMEText.MIMEText(body.encode('UTF-8'), 'plain', 'UTF-8')
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = email.Header.Header(subject, 'UTF-8')
        mailer = getUtility(IMailDelivery, 'my-app.mailer')
        mailer.send(sender, [recipient], msg.as_string())

In real-world code you may need to do extra work to format the 'From' and 'To'
headers correctly, if the addresses contain a real-name part with non-ASCII
characters.  You can find a recipe for that in this blog post:
http://mg.pov.lt/blog/unicode-emails-in-python.html


Configuration
=============

The code above used a named :class:`~.IMailDelivery` utility.  It is your responsibility
to define one, as Zope 3 doesn't provide one by default.  You can define
an IMailDelivery utility in your site.zcml with a configuration directive::

    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:mail="http://namespaces.zope.org/mail"

        <mail:queuedDelivery
            name="my-app.mailer"
            permission="zope.Public"
            mailer="smtp"
            queuePath="var/mailqueue"
            />

    </configure>

The ``mail:queuedDelivery`` directive stores every email in a queue (a standard
Maildir folder on the file system in a given directory) and sends them from a
background thread.  There's an alternative directive, ``mail:directDelivery``,
that sends them from the same thread.  This may slow down transaction commits
(especially if the SMTP server is slow to respond) and increase the loading
time of web pages.


Mailers
=======

The ``mailer`` argument of the ``mail:queuedDelivery`` utility chooses the
appropriate IMailer utility that will be used to deliver email.  There
are alternative ways of doing that, for example, SMTP or piping the message to
an external program.  Currently ``zope.sendmail`` supports only plain SMTP.
[#]_

.. [#] There was once a mailer utility that invoked /usr/sbin/sendmail, but
       it had security issues related to the difficulty of quoting command-line
       arguments in a portable way.

If the same system that runs your Zope 3 server also has an SMTP server on
port 25, you can use the default ``smtp`` mailer.  If you want to use a
different SMTP server, define your own utility like this::

    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:mail="http://namespaces.zope.org/mail"

        <mail:smtpMailer
            name="my-app.smtp"
            hostname="mail.my-app.com"
            port="25"
            />

        <mail:queuedDelivery
            name="my-app.mailer"
            permission="zope.Public"
            mailer="my-app.smtp"
            queuepath="var/mailqueue"
            />

    </configure>


Testing
=======

Obviously, you don't want your automated unit/functional test runs to send
real emails.  You'll have to define a fake email delivery utility in your
test layer.  Something like this will do the trick::

    @implements(IMailDelivery)
    class FakeMailDelivery(object):

        def send(self, source, dest, body):
            print("*** Sending email from %s to %s:" % (source, dest))
            print(body)
            return 'fake-message-id@example.com'

Register it with the standard ``utility`` directive::

    <utility name="my-app.mailer" factory="my-app.testing.FakeMailDelivery" />


Problems with zope.sendmail
===========================

* The API is a bit inconvenient to use (e.g. you have to do the message
  formatting by yourself).

* The configuration should be done in zope.conf, not in ZCML.
