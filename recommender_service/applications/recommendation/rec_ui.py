import datetime
import json
from collections import OrderedDict

import requests
from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from applications.common.lib import filter_by_key
from applications.recommendation.models import ContentSeen, Recommendation, Content
from applications.common.constant import MOU, CONTENT_SEEN_LIMIT, RCF, REC_MINLIMIT
from applications.recommendation.serializer import ContentSeenSerializer
from applications.recommendation.utils import RecommendationGenerator
from applications.recommendation.views import ContentSeenViewSet
from recommender_service.settings import JSON_SETTING
import logging
LOGGER = logging.getLogger("recommender_service.applications.recommendation.rec_ui")

@api_view(['POST','GET'])
@authentication_classes((SessionAuthentication,TokenAuthentication ))
@permission_classes((IsAuthenticated,))
def test(request,**kwargs):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    user_id=body.get('user_id') if body.get('user_id') else "None"
    recommendation_bucket=body.get("recommendation_bucket")
    content_id = body.get('content_id')
    content_id =content_id if content_id else "None"
    table1,table2={},{}
    params = {}
    print(recommendation_bucket)
    params['include_recency'] = True if 'recency'in recommendation_bucket else False
    params['include_mou']=True if 'mou' in recommendation_bucket else False
    recommendation_bucket ="recommendation_by_recency"
    print(params)
    if recommendation_bucket!='recommendation_by_recency':
        domain = "http://"+request.get_host()+"/"
        sub_url = "recommendation/v1/list/"+str(user_id)+"/"+str(recommendation_bucket)+"/"+str(content_id)
        url= domain+sub_url
        resp=requests.get(url)
        results = resp.json()
        results = results.get('results')
        if results:
            table2["heading"] = "Recommendation."
            table2["results"] = results
        content_seen = filter_by_key(ContentSeen, user_id=user_id, mou__gte=MOU).order_by('-date').values()[
                       :CONTENT_SEEN_LIMIT]
        content_seen = ContentSeenSerializer(content_seen,many=True).data
        if content_seen:
            table1['heading'] = "Content Seen By user."
            table1['results'] = content_seen
        response = render(request,'recommendation/recomm.html',{'table1':table1,"table2":table2})
        return  response
    INDEX, PAGE_SIZE = 0,100
    filter = {}
    recomm_id = RecommendationGenerator.decide(user_id, recommendation_bucket)
    content_seen_list = ContentSeenViewSet.content_seen_list(user_id, recomm_id)
    content_seen = content_seen_list[2]
    default = RecommendationGenerator.default(content_seen_list, filter=filter)
    contents = [recomm.content_recommended for recomm in default][INDEX:PAGE_SIZE]
    content_seen = list(map(lambda x: {'content_id': x.content_id, 'date': x.date, 'mou': float(x.mou)}, content_seen))
    recommendations = RecommendationGenerator.generate(recomm_id, content_seen_list, filter=filter)
    if not recommendations:
        table2['heading']="No Recommendation."
        response = render(request, 'recommendation/recomm.html', {'table1': table1, "table2": table2})
        return response
    recommendations = list(map( lambda recomm: {'content_seen': recomm.content_seen, 'content_recommended': recomm.content_recommended,
                        'confidence': float(recomm.confidence)}, recommendations))
    import pandas as pd
    try:
        df1 = pd.DataFrame(recommendations, columns=['content_seen', 'content_recommended', 'confidence'], dtype=object)
        df2 = pd.DataFrame(content_seen, dtype=object)
        df2['content_id'] = df2['content_id'].apply(str)
        df2['mou'] = df2['mou'] ** (1/3)
        df1['content_seen'] = df1['content_seen'].apply(str)
        df = pd.merge(df1, df2, how='left', left_on='content_seen', right_on='content_id')
        df = df.drop(columns='content_id')
        d1 = datetime.datetime.now().date()
        df['confidence'] = df.apply(lambda row: row['confidence'] * ((RCF / ((d1 - row['date'].date()).days + 1) if (d1 - row['date'].date()).days < RCF else 1)), axis=1) if params['include_recency'] else df['confidence']
        df['confidence'] = df['confidence'] * df['mou'] if params['include_mou'] else df['confidence']
        df = df[['content_seen', 'content_recommended', 'confidence']]
        df.sort_values(by=['confidence'], ascending=False, axis=0, inplace=True)
        recommendations = list(map(lambda x: Recommendation(**x), df.to_dict('records',OrderedDict)))
        recommendations = RecommendationGenerator.remove_duplicates(recommendations)
        recommendations = recommendations[INDEX:PAGE_SIZE]
        if len(recommendations) < REC_MINLIMIT:
            LOGGER.debug("length is less than 10 adding default.")
            recommendations = default
    except Exception as e:
        LOGGER.exception(e)
        recommendations = default
    recomm = convert_to_dict(recommendations)
    import pandas as pd
    try:
        df1= pd.DataFrame(recomm)
        content_ids = df1['content_recommended'].tolist()
        content_detail = filter_by_key(Content, content_id__in=content_ids).values()
        content_detail = list(content_detail) if content_detail else []
        df2 = pd.DataFrame(content_detail, dtype=object)
        content_ids = df1['content_seen'].tolist()
        content_detail = filter_by_key(Content, content_id__in=content_ids).values()
        content_detail = list(content_detail) if content_detail else []
        df3 = pd.DataFrame(content_detail, dtype=object)
        df1=pd.merge(df1,df2,left_on='content_recommended',right_on='content_id',how='left')
        df1.rename(columns={'content_name':'content_recommended_name','language':'content_recommened_lang'},inplace=True)
        df1=pd.merge(df1,df3,left_on='content_seen',right_on='content_id',how='left')
        df1.rename(columns={'content_name': 'content_seen_name','language':'content_seen_lang'}, inplace=True)
        df1.fillna('NA',inplace=True)
        columns = ['content_seen_name','content_seen_lang','content_recommended_name','content_recommened_lang','confidence']
        df1 = df1[columns]
        df1.rename(inplace=True,columns={'content_seen_name':'Content Watched','content_seen_lang':'Content Watched Language','content_recommended_name':'Content Recommended','content_recommened_lang':'Content Recommended Language','confidence':' Composite Score'})
    #for table 1
        content_seen = content_seen_list[2]
        content_seen = list(
            map(lambda x: {'user_id': x.user_id, 'content_id': x.content_id, 'date': x.date, 'mou': float(x.mou)},
                content_seen))
        df2 = pd.DataFrame(content_seen, dtype=object)
        content_detail = filter_by_key(Content, content_id__in=df2['content_id'].tolist()).values()
        content_detail = list(content_detail) if content_detail else []
        df3 = pd.DataFrame(content_detail, dtype=object)
        df = pd.merge(df2, df3, left_on='content_id', right_on='content_id', how='left')
        df = df[['user_id', 'content_id', 'content_name', 'date', 'mou']]
        df.fillna('NA', inplace=True)
        content_seen = df.to_dict('records', OrderedDict)
        if content_seen:
            table1['heading'] = "Content Seen By user."
            table1['results'] = content_seen
    except Exception as e:
        LOGGER.exception(e)
    table2 ={'heading':"content_recommened",'results':df1.to_dict('records',OrderedDict)}
    response = render(request, 'recommendation/recomm.html', {'table1': table1, "table2": table2})
    return response

def convert_to_dict(recomm):
        temp =[]
        for val in recomm:
            results = {}
            results ['content_seen'] = val.content_seen if hasattr(val,'content_seen') else 'default'
            results['content_recommended'] = val.content_recommended
            results ['confidence']=val.confidence
            temp.append(results)
        return temp