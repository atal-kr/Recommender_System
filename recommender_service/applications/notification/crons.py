from django_cron import CronJobBase, Schedule
from applications.notification.utils import NotificationUtils
from applications.notification.tasks import update_and_send

class PersonaNotificationCron(CronJobBase):
    """
        Cron Job for the Personalized notifications
    """
    RUN_EVERY_MINS = 5  # every 1 minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'notification.personal_notifications'    # a unique codeta

    def do(self):
        user_list=NotificationUtils.user_list_for_notification(from_csv=True)
        #NotificationUtils.personal_notifications(user_filter=user_list)
        length = len(user_list)
        for i in range(10):
            users = user_list[int((i * 0.1) * length):int(((i + 1) * 0.1) * length)]
            if users:
                 update_and_send.delay(users)
