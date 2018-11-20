"""
    Contains utility functions for the recommended notification
"""
import csv
import os
from django.db import transaction
from applications.common.constant import NO_OF_DAYS
from applications.notification.models import Recommended_Notification, Notification_History
import requests
from django.conf import settings
from applications.notification.clevertap_utils import CleverTapApis
from django.core.paginator import Paginator
import datetime
import logging
from applications.common.lib import filter_by_key
from applications.recommendation.models import ContentSeen
LOGGER= logging.getLogger('recommender_service.applications.notification.utils')

class NotificationUtils(object):
    """
        Contains functions for push notifications
    """

    @classmethod
    def personal_notifications(cls, **kwargs):
        """
            :param kwargs - Below parameters supported:
                :param user_filter - List of user Ids
                :param content_filter - List of content Ids
            Sends recommended personalized content notifications to users
        """
        assert settings.NOTIFICATION['enabled'], 'Global notification is disabled.'
        clever_api = CleverTapApis()
        data = cls.get_notification_data(**kwargs)
        headers = {'clientKey': settings.NOTIFICATION['clientKey'],
                   'X--platform': "Android",
                   'X--AppVersion': "53"}
        querystring = {"fields": "videos,videoInfo,images"}
        for d in data:
            response = requests.request("GET",
                                        settings.NOTIFICATION['content_details_url'] % d['content_id'],
                                        headers=headers,
                                        params=querystring)
            print(settings.NOTIFICATION['content_details_url'] % d['content_id'])
            if response.status_code == 200:
                response_data = response.json()
                # print '================'
                # print '================'
                if response_data['status'] == 'SUCCESS' and response_data.get('results') and response_data['results'][0]['videos']['status'] == 'SUCCESS':
                    #content_url = response_data['results'][0]['videos']['values'][0]['link']
                    notification_details = cls.get_notification_details(response_data,**kwargs)
                    title = notification_details['title']
                    body =  notification_details['body']
                    imageUrl = notification_details['imageUrl']
                    pagination_obj = Paginator(d['users'], 1000)
                    android_payload = {#'deep_link': content_url,
                                       '_id': d['content_id'],
                                       'action': 'autoplay',
                                       'imageUrl': imageUrl,
                                       'nid': datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                                       }
                    for page_no in pagination_obj.page_range:
                        p = pagination_obj.page(page_no)
                        LOGGER.info("#####################################################")
                        api_status,api_data = clever_api.send_push_notifications(identities=p.object_list,
                                                                 title=title,
                                                                 body=body,
                                                                 android_payload=android_payload)

                        LOGGER.info("status_code={} and response= {}".format(api_status,api_data))
                        LOGGER.info("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                        if api_status == 200 and api_data.get('status') == 'success':
                            with transaction.atomic():
                                for user in p.object_list:
                                    Notification_History(user_id=user, content_id=d['content_id']).save()
                else :
                    LOGGER.info("content store results :{}  ".format(response_data))
                    error ={
                        'content_id':d['content_id'],
                        'error': str(response_data)
                    }
                    filename = settings.FILE_DIR+'media/failed_notification.csv'
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    with open(filename, 'a+') as f:
                        writer = csv.writer(f)
                        writer.writerow([d['content_id'], str(response_data),str()])


    @classmethod
    def get_notification_data(cls, user_filter=None, content_filter=None, **kwargs):
        """
        :param users_filter - List of user Ids
        :param content_filter - List of content Ids
        :return: Arranged data from Recommended_Notification
        """

        filters = {}
        if user_filter:
            filters['user_id__in'] = user_filter
        if content_filter:
            filters['content_id__in'] = content_filter
        if filters:
            content_records = Recommended_Notification.objects.filter(**filters)
        else:
            content_records = Recommended_Notification.objects.all()
        content_records = content_records.order_by('-modified')
        data = []
        # exclude_users = []
        exclude_content_ids = []
        for content_obj in content_records:
            if content_obj.content_id not in exclude_content_ids:
                exclude_content_ids.append(content_obj.content_id)
                temp = {}
                temp['content_id'] = content_obj.content_id
                user_ids = list(content_records.filter(content_id=content_obj.content_id).values_list('user_id', flat=True))
                temp['users'] = user_ids
                # exclude_users += user_ids
                if user_ids:
                    data.append(temp)
        return data

    @classmethod
    def get_notification_details(cls,content_details=None,**kwargs):
        notification_details = {
            'title':None,
            'body': None,
            'imageUrl':None
        }
        notification_details.update(**kwargs)
        title = settings.NOTIFICATION.get('title') + " - " + content_details['results'][0]['generalInfo']['title'] if settings.NOTIFICATION.get('title') else content_details['results'][0]['generalInfo']['title']
        body = settings.NOTIFICATION.get('body') if settings.NOTIFICATION.get('body') else content_details['results'][0]['generalInfo']['briefDescription']
        imageUrl = settings.NOTIFICATION.get('imageUrl') if settings.NOTIFICATION.get('imageUrl') else cls.get_image_url(content_details['results'][0]['images']['values'])
        if not notification_details.get('title'):
            notification_details.update(title=title)
        if not notification_details['body']:
            notification_details.update(body=body)
        if not notification_details['imageUrl']:
            notification_details.update(imageUrl=imageUrl)
        return notification_details


    @classmethod
    def get_image_url(cls, images_list):
        """

        :return: get image url of 640*360 or 288x384
        """
        sizes = ['640x360', '288x384']
        types = ['banner', 'coverposter', 'portraitcoverposter']
        for sz in sizes:
            for tp in types:
                image_data = filter(lambda x: x['resolution'] == sz and x['type'] == tp, images_list)
                image_data = list(image_data)
                if image_data:
                    return image_data[0]['link']
        return ''


    @classmethod
    def user_list_for_notification(cls,**kwargs):
        """
        get all user for sending notification.
        :param kwargs:
        :return: list of user
        """
        from_csv = False
        #users=User.objects.values_list('user_id', flat=True)
        for key,value in kwargs.items():
            if key in 'from_csv':
                from_csv =value
        if from_csv:
            BASE_DIR = settings.FILE_DIR
            with open(BASE_DIR + '/media/user_list.csv', 'r+') as f:
                data = csv.reader(f)
                next(data)
                users = [row[0] for row in data]
        else:
            d = datetime.datetime.now() - datetime.timedelta(days=NO_OF_DAYS)
            print(d)
            users = filter_by_key(ContentSeen, date__gte=d)
            users =users.values_list('user_id', flat=True).distinct()
        return users

    @classmethod
    def chunks(cls,iterable,chunk_size):
        for i in range(0, len(iterable), chunk_size):
            yield iterable[i:i + chunk_size]

class Progress_Observer(object):
    total_work = None
    work_done =None
    def set_progress(self,work_done,total):
        self.work_done =work_done
        self.total_work =self.total_work
    def get_progress(self):
        percent = (self.work_done*100)/self.total_work
        return int(percent)
