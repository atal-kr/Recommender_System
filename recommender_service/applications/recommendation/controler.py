import logging
from random import shuffle
from rest_framework import viewsets, status
from rest_framework.response import Response
from applications.common.constant import BUCKET
from applications.recommendation.REViewSet import RecommendationViewSet
from applications.recommendation.models import Recommendation, Recommendation_Content
from applications.recommendation.utils import personalized_attr, get_for_coldstart_ab, personalization_by_taget_user, \
    personalization_by_content_id
from applications.recommendation.views import ContentViewSet
LOGGER = logging.getLogger('recommender_service.apps.recommendation.controller')

BUCKET_MAP = {
                'recommended for you' : 1,
                'recommended_for_you' :1,
                'recommendation_by_recency':2,
                'recommended_tv_show':3,
                'banner_by_circle':4,
                'banner':4,
                'similar_content_by_meta':5,
                'similar_content':5,
                'circle_live':6,
                'circle_movie':6,
                'because_you_watch':7,
                'automated_mass_personalization':8,
                'recommended_movie_show':9
            }


class RecommendationController(RecommendationViewSet):

    """it can control request comming to recommendation engine.    """
    def get(self, request, user_id, recommendation_bucket,*var,**kwargs):
        self.personalization ={}
        [self.personalization.update(personalized_attr(request)) if request.method=='GET' else '']
        """get recommendation related content based on bucket."""
        LOGGER.info("========================================================================")
        INDEX, PAGE_SIZE = self.index_count(request)

        class Switcher(RecommendationController):
            @classmethod
            def switch(cls, bucket):
                suffix = BUCKET_MAP.get(bucket.lower(),"")
                method_name = '_' + str(suffix) if suffix else '_default'
                method = getattr(cls, method_name)
                return method()
            @classmethod
            def _1(cls):
                recommendation_bucket = "Recommended For You"
                content_ids = get_for_coldstart_ab(user_id, recommendation_bucket)[INDEX:PAGE_SIZE]
                if not content_ids:
                    content_ids = self.get_recommendation(request, user_id, recommendation_bucket)
                return content_ids
            @classmethod
            def _2(cls):
                content_ids = get_for_coldstart_ab(user_id, recommendation_bucket)[INDEX:PAGE_SIZE]
                model= {'recomm_model': 'TVRecommendation', 'default': 'Coldstart_tv'} if self.personalization.get('content_type')=='tv_show' else {'recomm_model': 'Recommendation', 'default': 'Coldstart'}
                if not content_ids :
                    content_ids = self.recommendation_by_recency(request, user_id, recommendation_bucket,model=model)
                return content_ids
            @classmethod
            def _3(cls):
                models = {'recomm_model': 'TVRecommendation', 'default': 'Coldstart_tv'}
                content_ids = self.get_recommendation(request, user_id, recommendation_bucket, content_type="tv_show",models=models)
                return content_ids
            @classmethod
            def _4(cls):
                banner_type = recommendation_bucket.split("_")[-1] if "_" in recommendation_bucket else None
                content_ids = self.get_banner(request, user_id, banner_type=banner_type)
                return content_ids
            @classmethod
            def _5(cls):
                model = 'Recommendation_Content' if recommendation_bucket == 'similar_content_by_meta' else 'Recommendation'
                content_id = kwargs.get('content_id')
                content_ids = self.similar_content(request, user_id, content_id, model=model)
                return content_ids
            @classmethod
            def _6(cls):
                content_type = recommendation_bucket.split("_")[-1] if "_" in recommendation_bucket else \
                    recommendation_bucket.split(" ")[-1]
                content_ids = self.content_by_circle(request, user_id, content_type)
                return content_ids
            @classmethod
            def _7(cls):
                content_ids = self.beacuse_you_watch(request, user_id)
                return content_ids
            @classmethod
            def _8(cls):
                content_ids = self.mass_personalization(request,user_id)
                return content_ids
            @classmethod
            def _9(cls):
                models = {'recomm_model': ['Recommendation', 'TVRecommendation'],'default': ['Coldstart_tv', 'Coldstart']}
                content_ids = self.combined_recommendation(request,user_id,models=models)
                return content_ids
            @classmethod
            def _default(cls):
                msg = "bucket name is incorrect.it should be in %s" % str(BUCKET)
                return Response({"code": 404, "status": "FAILED", "message": msg}, status=status.HTTP_404_NOT_FOUND)
        content_ids = personalization_by_content_id(user_id,personalization=self.personalization) if self.personalization.get('content_id',None) else None
        if content_ids:
            [shuffle(content_ids) if self.personalization.get('randomization') else content_ids]
            response = ContentViewSet.get(content_ids)
            return response
        results = Switcher.switch(recommendation_bucket) if personalization_by_taget_user(user_id,personalization=self.personalization)  else []
        if isinstance(results, Response):
            return results
        [shuffle(results) if self.personalization.get('randomization') else results]
        response = ContentViewSet.get(results)
        return response











