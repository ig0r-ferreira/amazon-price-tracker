from email.message import EmailMessage
from smtplib import SMTP


def make_message(
    from_address: str,
    to_address: str | list[str],
    subject: str = 'No subject',
    body: str = '',
    content_type: str = 'plain',
) -> EmailMessage:
    msg = EmailMessage()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    if content_type not in ('plain', 'html'):
        raise ValueError(f'{content_type!a} is an unknown content type.')

    msg.add_alternative(body, subtype=content_type)

    return msg


class EmailClient:
    def __init__(
        self,
        smtp_server: SMTP,
        credentials: tuple[str, str],
    ):
        self._server = smtp_server
        host, port = str(getattr(smtp_server, '_host')).split(':')
        self._host = host
        self._port = int(port)
        self._login, self._password = credentials

    def _connect(self) -> None:
        self._server.connect(self._host, self._port)
        self._server.starttls()
        self._server.login(self._login, self._password)

    def _quit(self) -> None:
        self._server.quit()

    def send_message(self, msg: EmailMessage) -> None:
        self._connect()
        self._server.sendmail(
            from_addr=msg['From'], to_addrs=msg['To'], msg=msg.as_string()
        )
        self._quit()
