import requests
from django.conf import settings
import logging
LOGGER = logging.getLogger('recommender_service.applications.notification.clavertap_utils')

class CleverTapApis(object):
    """
        Interface for CleverTap apis
    """
    ACCOUNT_ID = settings.NOTIFICATION['services']['cleverTap']['ACCOUNT_ID']
    PASS_CODE = settings.NOTIFICATION['services']['cleverTap']['PASS_CODE']
    PUSH_URL = settings.NOTIFICATION['services']['cleverTap']['PUSH_URL']
    # EMAIL_URL = 'https://in.api.clevertap.com/1/send/email.json'
    SENDER_NAME = settings.NOTIFICATION['services']['cleverTap']['SENDER_NAME']

    def __init__(self):
        super(CleverTapApis, self).__init__()
        assert settings.NOTIFICATION['services']['cleverTap']['ENABLED'], 'CleverTap notification is disabled.'

    def get_headers(self, extra_headers=None):
        """

        :param extra_headers:
        :return: Function will return default headers along with the extra headers
        """
        headers = {'X-CleverTap-Account-Id': self.ACCOUNT_ID,
                   'X-CleverTap-Passcode': self.PASS_CODE,
                   'Content-Type': 'application/json'}
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def send_push_notifications(self, identities, title, body,
                                android_payload=None,
                                ios_payload=None, extra_headers=None):
        """

        :param identities: User identifiers for users [List]
        :param title: Title of notification
        :param body: Body/message of notification
        :param android_payload: Android payload
        :param ios_payload: IOS payload
        :param extra_headers: Extra headers can be sent in dictionary

        Sends push notifications to users
        """
        data = {"to": {"Identity": identities},
                "tag_group": "Push Notification",
                "respect_frequency_caps": False,
                "content": {
                    "title": title,
                    "body": body,
                    "platform_specific": {
                        "ios": {},
                        "android": {}
                    }
                }
               }
        if android_payload:
            data['content']['platform_specific']['android'].update(android_payload)
        if ios_payload:
            data['content']['platform_specific']['ios'].update(ios_payload)
        # print data['to']
        r = requests.post(self.PUSH_URL, json=data, headers=self.get_headers(extra_headers))
        LOGGER.info("url :{} , headers:{} ,data : {}".format(self.PUSH_URL,self.get_headers(extra_headers),data))
        return r.status_code, r.json()

    # def send_push_emails(self, identities, subject, message, extra_headers=None):
    #     """
    #
    #     :param identities: User identifiers for users [List]
    #     :param subject: Subject of email
    #     :param messsage: Html content of email i.e body
    #     :param extra_headers: Extra headers can be sent
    #     :return: Sends push email to users
    #     """
    #     data = {"to": {"Identity": identities},
    #             "tag_group": "Push Email",
    #             "respect_frequency_caps": False,
    #             "content": {
    #                 "subject": subject,
    #                 "body": message,
    #                 "sender_name": self.SENDER_NAME
    #             }
    #            }
    #     r = requests.post(self.EMAIL_URL, json=data, headers=self.get_headers(extra_headers))
    #     return r.status_code, r.json()


# s = CleverTapApis()
# print s.send_push_notifications(identities=['9527314944'])
# print s.send_push_emails(identities=['sourabh.soni@apalya.com'],
#                          subject='Test mail',
#                          message='<b>This is test mail.</b>')