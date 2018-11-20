# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import datetime
from django.utils.timezone import utc

now = datetime.datetime.utcnow().replace(tzinfo=utc)
# Create your models here.

class Recommended_Notification(models.Model):
    """
        Dummy table for personalized notification
    """
    user_id = models.BigIntegerField(unique=True,db_index=True)
    content_id = models.CharField(max_length=30,db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def create_or_update(self,*args,**kwargs):
            queryset,_ =Recommended_Notification.objects.update_or_create(user_id=self.user_id,defaults={'content_id':self.content_id})



    class Meta:
        db_table = 'recommended_notification'

class Notification_History(models.Model):
    user_id = models.BigIntegerField(db_index=True)
    content_id = models.CharField(max_length=30, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'notification_history'