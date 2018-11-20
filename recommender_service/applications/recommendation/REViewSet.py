import datetime
import itertools
import logging
from random import shuffle
from recommender_service import  settings
from collections import OrderedDict
import time
from django.apps import apps
from rest_framework import viewsets
from applications.common.constant import REC_MINLIMIT, REC_MAXLIMIT, RECOMMENDATION_ENGINE, \
    LIVE_LIMIT, RCF
from applications.common.lib import filter_by_key
from applications.recommendation.utils import RecommendationGenerator
from applications.recommendation.views import ContentSeenViewSet, UserViewSet
from .models import Recommendation, Banner, RecommendationAll, BannerContent, ContentAll
LOGGER = logging.getLogger('recommender_service.apps.recommendation.REViewset')

class RecommendationViewSet(viewsets.ViewSet):

    def get_recommendation(self,request,user_id,recommendation_bucket,**kwargs):
        INDEX,PAGE_SIZE= self.index_count(request)
        filter = self.get_filter(request)
        models = kwargs.get('models') if kwargs.get('models') else {}
        """Get Recommendation For User Corrosponding to user_id and recommendation_bucket."""
        LOGGER.info("fetch recommendation for user_id : %s , recommendation-bucket : %s ",str(user_id),str(recommendation_bucket))
        LOGGER.info("request params are :{}".format(self.personalization))
        # 1.get recommendation_id corrosponding to user_gender,user_language,recommendation_bucket.
        recomm_id = RecommendationGenerator.decide(user_id,recommendation_bucket)
        LOGGER.debug("recomm_id for user : %s  is %s",str(user_id),str(recomm_id))
        # 2.get conteen_seen by user
        content_seen_list = ContentSeenViewSet.content_seen_list(user_id,recomm_id,content_type=kwargs.get('content_type')) # list of content seen having recommendation
        content_seen_list[1] = content_seen_list[1] if  self.personalization.get('remove_content_seen',True) else []
        LOGGER.debug("content seen by user :%s is :%s",str(user_id),str(content_seen_list[1]))
        # 3.get recommendation excluding content seen by user
        recommendations = RecommendationGenerator.generate(recomm_id,content_seen_list,filter=filter,model=models.get('recomm_model'))
        # 4.remove recommendation having lower confidence
        recommendations = RecommendationGenerator.remove_duplicates(recommendations)
        # 5.if length of recommendation is less than 10 then add from coldstart
        if len(recommendations)< REC_MINLIMIT:
            LOGGER.debug("len of recommendation is %d which is less than min Limit %s.",len(recommendations),REC_MINLIMIT)
            default = RecommendationGenerator.default(content_seen_list,filter=filter,model=models.get('default'))
            recommendations += default
            LOGGER.debug("coldstart %d recommendation  added.",len(default))
        recommendations =   recommendations[INDEX:PAGE_SIZE]
        recommendations = [recomm.content_recommended for recomm in recommendations]
        LOGGER.debug("recommendations is: {}".format(recommendations))
        return recommendations

    def get_banner(self,request,user_id,**kwargs):
        """get list of content for banner."""
        LOGGER.info("request params are :{}".format(self.personalization))
        banner_type = kwargs.get("banner_type")
        INDEX, PAGE_SIZE = self.index_count(request)
        order_by = self.personalization.get('order_by', 'uu_played')
        if banner_type  and banner_type in  "circle_based":
            circle = UserViewSet.get_user_circle(user_id)
            circle = circle if circle else 'all'
            contents = filter_by_key(BannerContent, circle=circle,recomm_id=self.personalization.get("recommendation_id",1)).order_by('-'+order_by)[:REC_MAXLIMIT]
            contents = [value.content_id for value in contents if contents][INDEX:PAGE_SIZE]
            if len(contents)<REC_MINLIMIT:
                LOGGER.debug("length of banner content is {} is less than min limit {}".format(len(contents),REC_MINLIMIT))
                LOGGER.debug("adding default content for banner with circle: all")
                contents = filter_by_key(BannerContent, circle='all').order_by('-'+order_by)[:REC_MAXLIMIT]
                contents = [value.content_id for value in contents if contents][INDEX:PAGE_SIZE]
            LOGGER.debug("banner contents are: {}".format(contents))
            return contents
        LOGGER.info("request to get banner . user_id : %s",user_id)
        content_seen_list = ContentSeenViewSet.content_seen_list(user_id)
        banners = filter_by_key(Banner).order_by('-'+order_by).exclude(content_recommended__in = content_seen_list[1])[:REC_MAXLIMIT]
        banners = list(banners) if banners else []
        LOGGER.debug("len of banner : %d",len(banners))
        banners = RecommendationGenerator.remove_duplicates(banners)
        banners = banners[INDEX:PAGE_SIZE]
        banners = [banner.content_recommended for banner in banners]
        LOGGER.debug("banner contents are: {}".format(banners))
        return banners

    def similar_content(self,request,user_id,content_id,model='Recommendation'):
        """get content similar to specific content."""
        INDEX, PAGE_SIZE = self.index_count(request)
        LOGGER.info("request params are :{}".format(self.personalization))
        LOGGER.info("get simmilar content for content_id : %s and user_id :%s",content_id,user_id)
        content_seen_list = ContentSeenViewSet.content_seen_list(user_id)
        content_seen_list[1] = content_seen_list[1] if self.personalization.get('remove_content_seen', True) else []
        LOGGER.debug("content seen by user {}".format(content_seen_list[1]))
        model = apps.get_model('recommendation', model)
        order_by = self.personalization.get('order_by','confidence')
        similar_contents = filter_by_key(model,content_seen=content_id).order_by('-'+order_by).exclude(content_recommended__in = content_seen_list[1])
        similar_contents= list(similar_contents) if similar_contents else []
        if len(similar_contents) < REC_MINLIMIT:
            LOGGER.debug("length of similar contents  is %s which is less than min limit %s",len(similar_contents),str(REC_MINLIMIT))
            default =RecommendationGenerator.default(content_seen_list=content_seen_list)
            similar_contents += default
            LOGGER.debug("added from coldstart : %d",len(default))
            return []
        similar_contents = similar_contents[INDEX:PAGE_SIZE]
        contents = [value.content_recommended for value in similar_contents]
        LOGGER.debug("similar_content for content_id :{} is {}".format(content_id,contents))
        return contents

    def get_from_recommendation_all(self,request,user_id,recommendation_bucket):
        """get recommendation for bucket meva_recommended_movies"""
        INDEX, PAGE_SIZE = self.index_count(request)
        LOGGER.info("request params are :{}".format(self.personalization))
        content_type = self.personalization.get('recomm_type','movie')
        content_seen_list = ContentSeenViewSet.content_seen_list(user_id)
        content_seen_list[1] = content_seen_list[1] if self.personalization.get('remove_content_seen', True) else []
        order_by = self.personalization.get('order_by', 'recomm_score')
        queryset =filter_by_key(RecommendationAll,user_id =user_id,content_type=content_type).order_by('-'+order_by).exclude(content_id__in=content_seen_list[1] )[:REC_MAXLIMIT]
        content_id =[value.content_id for value in list(queryset)] if queryset else []
        if len(queryset) < REC_MINLIMIT:
            default = RecommendationGenerator.default(content_seen_list)
            content_id += [value.content_recommended for value in default]
        content_ids = content_id[INDEX:PAGE_SIZE]
        return content_ids

    def content_by_circle(self,request,user_id,content_type=None):
        """get top content of user's circle."""
        INDEX, PAGE_SIZE = self.index_count(request)
        LOGGER.info("request params are :{}".format(self.personalization))
        LOGGER.info("fetch top content by circle for user_id : %s and content_type: %s",user_id,content_type)
        if not content_type :
            content_type = RECOMMENDATION_ENGINE.get('CIRCLE_CONTENT_TYPE',"movies")
        #get the user circle
        circle = UserViewSet.get_user_circle(user_id)
        circle = circle if circle else 'all'
        LOGGER.debug('content_type : %s , circle : %s ',content_type,circle)
        content_seen_list=[[],[]]
        LIMIT = LIVE_LIMIT  if content_type is "live" else REC_MAXLIMIT
        if content_type != "live":
            content_seen_list = ContentSeenViewSet.content_seen_list(user_id)
            content_seen_list[1] = content_seen_list[1] if self.personalization.get('remove_content_seen', True) else []
            LOGGER.debug('content_seen by user {}'.format(content_seen_list[1]))
        order_by = self.personalization.get('order_by','uu_played')
        contents = filter_by_key(ContentAll,circle=circle,content_type=content_type).order_by('-'+order_by).exclude(content_id__in = content_seen_list[1])[:LIMIT]
        contents = [value.content_id for value in contents if contents]
        if content_type!='live' and  len(contents) < REC_MINLIMIT:
            LOGGER.debug("length of content: {} is less than mon limit:{} ".format(len(contents),REC_MINLIMIT))
            default = RecommendationGenerator.default(content_seen_list)[:REC_MAXLIMIT]
            contents += [recomm.content_recommended for recomm in default]
        elif len(contents) < REC_MINLIMIT:
            contents = filter_by_key(ContentAll, circle='all', content_type=content_type).order_by('-'+order_by).exclude(
                content_id__in=content_seen_list[1])[:LIMIT]
            contents = [value.content_id for value in contents if contents]
        contents = contents[INDEX:PAGE_SIZE]
        LOGGER.debug("circle contents are {}".format(contents))
        return contents

    def beacuse_you_watch(self,request,user_id):
        """ because you watch suggest user to watch similar content corrosponding to content watch by user"""
        LOGGER.info("for becuse u watch  user_id : %s",user_id)
        LOGGER.info("request params are :{}".format(self.personalization))
        # get last played content by user
        content_id = UserViewSet.last_played_content(user_id)
        LOGGER.debug("content Id for because U watch is %s",content_id)
        response = self.similar_content(request,user_id,content_id)
        return response

    def index_count(self,request):
        try:
            INDEX = int(request.GET.get('startIndex')) - 1 if request.GET.get('startIndex') else 0
            PAGE_SIZE = int(request.GET.get('count')) if request.GET.get('count') else 10
            INDEX = INDEX * PAGE_SIZE
            PAGE_SIZE = INDEX + PAGE_SIZE
        except :
            INDEX,PAGE_SIZE=0,10
        return [INDEX,PAGE_SIZE]

    def get_filter(self,request):
        my_filter = {}
        filter_on =RECOMMENDATION_ENGINE['RECOMM_FILTER']
        for key in filter_on:
            value =request.GET.getlist(key)
            if value:
                my_filter[key]=value
        LOGGER.info("filter is {}".format(my_filter))
        return my_filter

    def recommendation_by_recency(self,request,user_id,recommendation_bucket,**kwargs):
            """
            :param request: http request
            :param user_id: id of user
            :param recommendation_bucket: recommendation_by_recency
            :param kwargs:
            :return: list of recommended content_id
            """

            INDEX, PAGE_SIZE = self.index_count(request)

            filter = self.get_filter(request)
            LOGGER.info("request params are :{}".format(self.personalization))
            recomm_id = RecommendationGenerator.decide(user_id, recommendation_bucket)
            content_seen_list = ContentSeenViewSet.content_seen_list(user_id,recomm_id)
            content_seen = content_seen_list[2]
            content_seen_list[1] = content_seen_list[1] if   self.personalization.get('remove_content_seen',True) else []
            LOGGER.info("content_seen by user is {}".format(content_seen_list[0]))
            def defualt_content():
                default = RecommendationGenerator.default(content_seen_list,filter=filter,model=kwargs['model'].get('default'))
                contents = [recomm.content_recommended for recomm in default][INDEX:PAGE_SIZE]
                return contents
            content_seen = list(map(lambda x: {'content_id': x.content_id, 'date': x.date, 'mou': float(x.mou)}, content_seen))
            t1 = time.time()
            recommendations = RecommendationGenerator.generate(recomm_id, content_seen_list, filter=filter,model=kwargs['model'].get('recomm_model'))
            if not (content_seen and recommendations):
                LOGGER.info("user : {} has not seen any content or has no recommendation.delivering default. ".format(user_id))
                return defualt_content()
            recommendations = list(map(lambda recomm:{'content_seen':recomm.content_seen,'content_recommended':recomm.content_recommended,'confidence':float(recomm.confidence)}, recommendations))
            import pandas as pd
            try :
                df1= pd.DataFrame(recommendations,columns=['content_seen','content_recommended','confidence'],dtype=object)
                df2 = pd.DataFrame(content_seen,dtype=object)
                df2['content_id']= df2['content_id'].apply(str)
                df2['mou'] = df2['mou']**(1/3)
                df1['content_seen'] = df1['content_seen'].apply(str)
                df = pd.merge(df1,df2,how='left',left_on='content_seen',right_on='content_id')
                df=df.drop(columns='content_id')
                d1 = datetime.datetime.now().date()
                if self.personalization.get('recency',True):
                    df['confidence']=df.apply(lambda row:row['confidence']*((RCF/(((d1-row['date'].date())//7).days+1) if (d1-row['date'].date()).days<RCF else 1)),axis=1)
                    LOGGER.info("including recency to recommendation.")
                df['confidence']= df['confidence']*df['mou'] if self.personalization.get('include_duration',True) else df['confidence']
                df=df[['content_seen','content_recommended','confidence']]
                df.sort_values(by=self.personalization.get('order_by','confidence'), ascending=False, axis=0, inplace=True)
                LOGGER.info("sorting recommendation based on {}".format(self.personalization.get('order_by','confidence')))
                recommendations = list(map(lambda x: Recommendation(**x), df.to_dict('records',OrderedDict)))
                recommendations = RecommendationGenerator.remove_duplicates(recommendations)
                recommendations = recommendations[INDEX:PAGE_SIZE]
                recommendations = [recomm.content_recommended for recomm in recommendations]
                if len(recommendations)< REC_MINLIMIT:
                    LOGGER.debug("length of content for bucket {} is {} whiich is less than min limit".format(recommendation_bucket,len(defualt_content())))
                    return defualt_content()
                return recommendations
            except Exception as e:
                LOGGER.debug("Error in calculating recommendation.{}".format(e))
                return defualt_content()

    def mass_personalization(self,request,user_id,**kwargs):
        """
        :param request: request object
        :param user_id:
        :param kwargs:
        :return: list of content_id
        """
        LOGGER.info("get mass personalization contents.")
        # get user circle
        circle = UserViewSet.get_user_circle(user_id)
        INDEX, PAGE_SIZE = self.index_count(request)
        circle = circle if circle else 'all'
        p_data = {'circle':circle}
        LOGGER.info("request param is : {}".format(self.personalization))
        model = apps.get_model('recommendation', 'ContentAll')
        content_seen_list = ContentSeenViewSet.content_seen_list(user_id)
        content_seen_list[1] = content_seen_list[1] if self.personalization.get('remove_content_seen', True) else []
        for key in model._meta.fields:
            key = key.name
            if self.personalization.get(key):
                value = self.personalization.get(key)
                key = key if not isinstance(value,list) else key+"__in"
                p_data[key]= value
        order_by = self.personalization.get('order_by','uu_played')
        queryset = filter_by_key(model,**p_data).order_by('-'+order_by).exclude(content_id__in=content_seen_list[1])[INDEX:PAGE_SIZE]
        content_ids = list(queryset.values_list('content_id' ,flat=True)) if queryset else []
        return content_ids

    def combined_recommendation(self,request,user_id,**kwargs):
        """
        :param request:
        :param user_id:
        :param kwargs:
        :return: combination of recommended tv show and movie
        """
        INDEX, PAGE_SIZE = self.index_count(request)

        LOGGER.info("request params are :".format(self.personalization))
        filter = self.get_filter(request)
        content_seen_list = ContentSeenViewSet.content_seen_list(user_id)
        recommendations,default = [],[]
        for model in kwargs['models'].get("recomm_model"):
            recommendations.append(RecommendationGenerator.generate(1, content_seen_list, filter=filter,model=model))
        #mixed recommendation
        recommendations =[(a,b) for a,b in zip(*recommendations)]
        recommendations =list(itertools.chain(*recommendations))
        recommendations = RecommendationGenerator.remove_duplicates(recommendations)
        if len(recommendations)<REC_MINLIMIT:
            for model in kwargs['models'].get('default'):
                default.append( RecommendationGenerator.default(content_seen_list, filter=filter,model=model))
            default = [(a, b) for a, b in zip(*default)]
            default = list(itertools.chain(*default))
        recommendations +=  default
        shuffle(recommendations)
        recommendations =recommendations[INDEX:PAGE_SIZE]
        content_ids = [recomm.content_recommended for recomm in recommendations]
        LOGGER.debug("mixed recommendation are :{}".format(content_ids))
        return content_ids
