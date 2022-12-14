import logging
import os
from datetime import datetime
from typing import Any, Union

from celery import shared_task
from celery.signals import task_failure, task_success
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from mailservice.models.email import Email
from mailservice.models.mailbox import Mailbox


@shared_task(bind=True)
def send_email_task(
    self,
    mailbox: dict[str, Union[str, int]],
    template: dict[str, str],
    validated_data: dict[str, Any],
    filename: str,
    email_id: str,
) -> str:
    """Celery async task. Try to send mail based on provided data. In case of failure task is repeated 3 times. Errors are
    being logged into the email.log file"""
    try:
        with get_connection(
            host=mailbox.get("host"),
            port=mailbox.get("port"),
            username=mailbox.get("login"),
            password=mailbox.get("password"),
            use_ssl=mailbox.get("use_ssl"),
            use_tls=True,
        ) as connection:
            email = EmailMessage(
                template.get("subject"),
                template.get("text"),
                mailbox.get("email_from"),
                validated_data.get("to"),
                validated_data.get("bcc"),
                cc=validated_data.get("cc"),
                reply_to=[validated_data.get("reply_to")],
                connection=connection,
            )
            email.attach_file(filename)
            email.send()
    except Exception as e:
        logging.error(f"Sending mail {email_id} failed @ {datetime.now()}\n")
        raise self.retry(exc=e, countdown=1, max_retries=2)

    return email_id


@task_success.connect(sender=send_email_task)
def task_success_actions(sender, result, **kwargs):
    """Celery task send_email_task post-success actions. Sets datetime.now object to sent field of the Email model object.
    Modifies sent mail counter and last update datetime filed of corresponding Mailbox model object."""
    email = Email.objects.get(pk=result)
    email.sent_date = datetime.now()
    mailbox = email.mailbox
    mailbox.sent += 1
    mailbox.last_update = datetime.now()
    mailbox.save()
    email.save()
