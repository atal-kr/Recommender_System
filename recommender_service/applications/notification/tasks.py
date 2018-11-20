# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from applications.notification.utils import NotificationUtils
from applications.notification.views import Notification




@shared_task
def update_and_send(user_list):
    Notification.update_recomendation(user_list=user_list)
    NotificationUtils.personal_notifications(user_filter=user_list)

@shared_task
def send_notification(user_list):
    NotificationUtils.personal_notifications(user_filter=user_list)
    return 'done'

@shared_task
def update_notification(user_list):
    """update table to send notification"""
    Notification.update_recomendation(user_list=user_list)
    return 'done'

@shared_task
def sheduled_notification(**kwargs):
    from_csv = False
    for key,value in kwargs.items():
        if key == 'from_csv':
            from_csv = True
    user_list = NotificationUtils.user_list_for_notification(from_csv=from_csv)
    # NotificationUtils.personal_notifications(user_filter=user_list)
    length = len(user_list)
    for i in range(10):
        users = user_list[int((i * 0.1) * length):int(((i + 1) * 0.1) * length)]
        if users and from_csv:
            update_and_send.delay(users)
        elif users:
            send_notification.delay(users)


