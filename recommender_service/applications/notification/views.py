# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.db import transaction
from rest_framework.viewsets import ViewSet
from applications.notification.models import Recommended_Notification
# Create your views here.
from applications.recommendation.utils import RecommendationGenerator
from applications.recommendation.views import ContentSeenViewSet
from recommender_service import settings

LOGGER=logging.getLogger("recommender_service.applications.notification.views")

class Notification(ViewSet):

    @classmethod
    def update_recomendation(cls,**kwargs):
        # get recommendation_list for all  user
        LOGGER.info("update recommended notification.")
        from_csv = False
        user_list=None
        for key,value in kwargs.items():
            if key=='from_csv':
                from_csv = True
            if key=="user_list":
                user_list = value
        recomm_id = settings.NOTIFICATION['recommendation_id'][0] if settings.NOTIFICATION['recommendation_id'] else 1
        with transaction.atomic():
            for user_id in user_list:
                content_seen_list = ContentSeenViewSet.content_seen_list(user_id, recomm_id)
                recommendations = RecommendationGenerator.generate(recomm_id, content_seen_list)
                if recommendations:
                    content_id = recommendations[0].content_recommended
                    #queryset, _ = Recommended_Notification.objects.update_or_create(user_id=user_id, defaults={'content_id': content_id})
                    Recommended_Notification(user_id=user_id,content_id=content_id).save()


