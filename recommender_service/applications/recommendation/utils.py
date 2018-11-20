import json
import logging
from applications.common.lib import filter_by_key, get_by_key
from applications.recommendation.models import User, Decider, Content, ContentAll, get_coldstart, User_AB
from applications.common.constant import REC_MINLIMIT, REC_MAXLIMIT, DECIDER_ENABLE, COLADSTART_AB_ENABLE
from django.apps import apps
LOGGER = logging.getLogger('recommender_service.apps.recommendation.utils')

class RecommendationGenerator(object):
    """it is used to generate recommendations."""
    @classmethod
    def generate(cls,recomm_id,content_seen_list,**kwargs):
        """it will generate recommendation by removing content seen by user."""
        model = kwargs.get('model') if kwargs.get('model') else 'Recommendation'
        filter = kwargs.get('filter')
        model = apps.get_model('recommendation',model)
        queryset=filter_by_key(model,recomm_id=recomm_id,content_seen__in=content_seen_list[0]).exclude(content_recommended__in = content_seen_list[1])
        results =  cls.filter_recomm(on_queryset=queryset,my_filter=filter) if filter else list(queryset) if queryset else []
        results.sort(key=lambda obj: obj.confidence, reverse=True)
        results=results[:REC_MAXLIMIT]
        return results

    @classmethod
    def default(cls,content_seen_list = (),**kwargs):
        """it will generate default recommendation excluding content already seen by user."""
        model = kwargs.get('model') if kwargs.get('model') else 'Coldstart'
        filter = kwargs.get('filter')
        LOGGER.info("calling to coldtstart :{}".format(model))
        model=get_coldstart(model)
        if content_seen_list:
            queryset=filter_by_key(model).exclude(content_recommended__in = content_seen_list[1])
        else :
            queryset = filter_by_key(model)
        results = cls.filter_recomm(on_queryset=queryset, my_filter=filter) if filter else list(queryset) if queryset else []
        if not results or len(results) < REC_MINLIMIT:
            LOGGER.warn("forcefully adding coldstart.")
            queryset = filter_by_key(model)
            results = list(queryset) if queryset else []
        results = RecommendationGenerator.remove_duplicates(results)
        results.sort(key=lambda obj:obj.confidence,reverse=True)
        return results[:REC_MAXLIMIT]

    @classmethod
    def remove_duplicates(cls,recommendation_list):
        """it will remove duplicates recommendation having lower confidense."""
        unique_content_list = []
        for content in recommendation_list:
            try:
                if unique_content_list.__contains__(content):
                    index = unique_content_list.index(content)
                    temp = unique_content_list[index]
                    if temp.confidence < content.confidence:
                        unique_content_list.remove(temp)
                        unique_content_list.append(content)
                else:
                    unique_content_list.append(content)
            except:
                LOGGER.debug("error in comparing confidence for content having content seen id {}".format(content.content_seen_id))
        return unique_content_list

    @classmethod
    def decide(cls,user_id,recommendation_bucket):
        """it is used to decide recommendation_id for user based on user_gender,language and recommendation_bucket."""
        if DECIDER_ENABLE:
            try:
                user=get_by_key(User,user_id=user_id)
                user_language=user.language
                user_gender = user.gender
                queryset=filter_by_key(Decider,recomm_bucket=recommendation_bucket,gender=user_gender,language=user_language).values()
                return queryset['recommendation_bucket']
            except (User.DoesNotExist,KeyError,TypeError):
                LOGGER.error("error in decider.")
                return 0
        return 1

    @classmethod
    def filter_recomm(cls,on_queryset=None,my_filter=None,**kwargs):
        import pandas as pd
        if on_queryset :
            try:
                if hasattr(on_queryset.first(),'content_seen'):
                    left_data = list(map(lambda recomm:{'content_seen':recomm.content_seen,'content_recommended':recomm.content_recommended,'confidence':float(recomm.confidence)}, on_queryset))
                    result_keys =['content_seen','content_recommended','confidence']
                else:
                    left_data = list(map(lambda recomm: {'content_recommended': recomm.content_recommended,'confidence': recomm.confidence}, on_queryset))
                    result_keys = [ 'content_recommended', 'confidence']
                df1 =pd.DataFrame(left_data,dtype=object,columns=['content_seen','content_recommended','confidence'])
                df1['content_recommended']=df1['content_recommended'].apply(str)
                content_ids =set(df1['content_recommended'].tolist())
                content_detail = filter_by_key(Content,content_id__in=content_ids).values()
                content_detail = list(content_detail) if content_detail else []
                df2 = pd.DataFrame(content_detail,dtype=object)
                df2['content_id']=df2['content_id'].apply(str)
                df = pd.merge(df1,df2,left_on='content_recommended',right_on='content_id',how='left')
                df['language']=df['language'].apply(lambda lang:lang.split(',') if isinstance(lang,str) else lang)
                df['genre'] = df['genre'].apply(lambda gen: gen.split(';') if isinstance(gen, str) else gen)
                [my_filter.pop(key) for key in list(my_filter) if key not in list(df)]
                df=df.fillna('')
                idx=[]
                for key,value in my_filter.items():
                     temp = []
                     for i,lang in df[key].iteritems():
                            if set(lang) & set(value):
                                temp.append(i)
                     idx = list(set(temp) & set(idx)) if temp and idx else temp if temp else idx
                df=df.iloc[idx] if idx else df
                df=df[result_keys]
                df.sort_values(by=['confidence'], ascending=False, axis=0, inplace=True)
                results =list(map(lambda x:on_queryset.model(**x),df.to_dict('records')))
                return results
            except Exception as e:
                LOGGER.error("error in filtering recommendation:{}".format(e))
                return []
        return []



def personalized_attr(request):
    try:
        resp =json.loads(list(request.GET)[0])
    except :
        temp = dict(request.GET.copy())
        for key,val in temp.items():
            if len(val)==1:
                temp[key]=True if val[0].lower() in ['yes','true'] else False if val[0].lower() in ['no','false'] else val[0]
        resp = temp
    return resp



def get_for_coldstart_ab(user_id,bucket=None):
    if not COLADSTART_AB_ENABLE:
        return []
    user_list = list(User_AB.user_list())
    try:
        user_id = int(user_id)
    except:
        LOGGER.error("invalid user_id.")
    if user_id in user_list:
        content_id = get_coldstart('Coldstart_AB').get_content()
        return content_id
    return []


def personalization_by_content_id(user_id,**kwargs):
    personalization= kwargs.get('personalization',{})
    content_ids = personalization.get('content_id')
    content_ids = list(set(content_ids))
    #model = apps.get_model('recommendation', 'ContentAll')
    #sort the value based on UU_played
    #queryset = filter_by_key(model,content_id__in=content_ids,circle='all').order_by('uu_played')
    return content_ids


def personalization_by_taget_user(user_id,**kwargs):
    personalization = kwargs.get('personalization', {})
    target_audience ={} if not isinstance(personalization.get('target_audience',{}),dict) else personalization.get('target_audience',{})
    model =apps.get_model('recommendation','LastContentPlayed')
    user = filter_by_key(model, user_id=user_id).values()
    user = user[0] if user else []
    if not user:
        return True
    for key,val in target_audience.items():
        if not user.get(key)==val:
            return False
    return True










