# Create your views here.
import json
from _decimal import Decimal

from django.http import HttpResponse
from rest_framework_xml import parsers
from rest_framework.decorators import api_view, parser_classes
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status,  viewsets
import logging
from rest_framework_xml.parsers import XMLParser
from rest_framework.parsers import MultiPartParser, FormParser
from applications.notification.models import Notification_History
from applications.common.lib import get_by_key, filter_by_key
from .models import User, ContentSeen, Content, LastContentPlayed, UserAction
from .serializer import UserSerializer, ContentSeenSerializer, ContentSerializer, UserActionSerializer, \
    RecommendationSerializer, ContentWriteSerializer
from applications.common.response import Results
from applications.common.constant import CONTENT_SEEN_LIMIT, MOU
LOGGER = logging.getLogger('recommender_service.apps.recommendation.views')

class UserViewSet(viewsets.ViewSet,CreateAPIView):
    serializer_class = UserSerializer
    def get(self,request,user_id):
        """GET USER DETAILS.."""
        try:
            users=get_by_key(User,user_id=user_id)
            serializer_class = UserSerializer(users)
        except (User.DoesNotExist,Exception)as e:
            results=Results(404,"FAILED",message="User Does not Exixt.").serialize()
            return Response(results,status=status.HTTP_404_NOT_FOUND)
        results = Results(200,"SUCCESS",extra_field={"results":serializer_class.data}).serialize()
        return Response(results,status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Create User or Update details."""
        instance=get_by_key(User,user_id=request.data.get('user_id'))
        user,msg = UserSerializer(instance=instance,data=request.data),"User details updated." if instance else UserSerializer(data=request.data),"User created SuccessFully."
        if user.is_valid():
            user.save()
            results=Results(201,"SUCCESS",msg).serialize()
            return Response(results,status=status.HTTP_201_CREATED)
        return Response(user.errors,status=status.HTTP_400_BAD_REQUEST)

    def perform_action(self,request):
        action = UserActionSerializer(data=request.data)
        if action.is_valid():
            action.save()
            results = Results(200, "SUCCESS", "content added").serialize()
            return Response(results, status=status.HTTP_200_OK)
        results = Results(400, "FAIL", "unable to process your request right now.").serialize()
        return Response(results, status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def get_user_circle(cls,user_id):
        """return  user circle ."""
        circle = None
        queryset = filter_by_key(LastContentPlayed, user_id=user_id)[:1]
        if queryset:
            circle = queryset[0].circle
        return circle

    @classmethod
    def last_played_content(cls,user_id):
        "return content_id of last played content of user."
        content_id = None
        queryset = filter_by_key(LastContentPlayed, user_id=user_id)
        if queryset:
            content_id = queryset[0].content_id
        return content_id



class ContentSeenViewSet(viewsets.ViewSet,CreateAPIView):
        """GET CONTENT SEEN BY USER."""
        serializer_class = ContentSeenSerializer

        def get(self,request,user_id):
            """Get Content Seen By User."""
            content_seen_list = ContentSeenViewSet.content_seen_list(user_id,1)
            if content_seen_list and content_seen_list[0]:
                results=Results(200,"SUCCESS", extra_field={"results":content_seen_list[0]}).serialize()
                return Response(results,status=status.HTTP_200_OK)
            results = Results(404, "FAILED", "User has not seen any content.").serialize()
            return Response(results, status=status.HTTP_404_NOT_FOUND)

        def post(self, request, *args, **kwargs):
            """Update Stream History of User."""
            content_seen = get_by_key(ContentSeen,user_id=request.data.get('user_id'),content_id=request.data.get('content_id'))
            if content_seen:
                mou = content_seen.mou
                try:
                    request.data['mou']= Decimal(request.data.get('mou')) + mou
                except:
                    pass
                content_seen = ContentSeenSerializer(instance=content_seen,data=request.data)
            else :
                content_seen = ContentSeenSerializer(data=request.data)
            if content_seen.is_valid():
                content_seen.save()
                results = Results(201, "SUCCESS", "UserStreamingHistory updated Sucessfully.",{"results":content_seen.data}).serialize()
                return Response(results, status=status.HTTP_201_CREATED)
            return Response(content_seen.errors, status=status.HTTP_400_BAD_REQUEST)

        @classmethod
        def content_seen_list(cls,user_id,recomm_id=0,**kwargs):
            content_type = kwargs.get('content_type')
            effective, exclude = [], []
            queryset = filter_by_key(ContentSeen, user_id=user_id).order_by('-date')
            if content_type == 'tv_show':
                content_ids = cls.watched_tv_show(queryset.filter(mou__gte=MOU))
                return [content_ids, content_ids]
            queryset1 = queryset.filter(mou__gte=MOU).values_list('content_id', flat=True)[:CONTENT_SEEN_LIMIT]
            [effective.append(id) for id in queryset1 if id not in effective]
            excludes = queryset.values_list('content_id', flat=True)[:CONTENT_SEEN_LIMIT]
            disliked_content = filter_by_key(UserAction,user_id = user_id, action_id =1).values_list('content_id',flat=True).distinct()
            queryset2 = filter_by_key(Notification_History, user_id=user_id).values_list(
                'content_id', flat=True).distinct()[:CONTENT_SEEN_LIMIT]
            [exclude.extend(list(value)) for value in [excludes, queryset2] if value]
            exclude+=disliked_content
            return [effective, exclude, queryset.filter(mou__gte=MOU)[:CONTENT_SEEN_LIMIT]]

        @classmethod
        def watched_tv_show(self,watched_tv_show,**kwargs):
            import pandas as pd
            if not watched_tv_show:
                return []
            try:
                content_seen = list(map(lambda x: {'content_id': x.content_id, 'date': x.date, 'mou': float(x.mou) }, watched_tv_show))
                df1=pd.DataFrame(content_seen,dtype='object')
                content_ids = set(df1['content_id'].tolist())
                content_detail = filter_by_key(Content,content_id__in=content_ids).values()
                content_detail = list(content_detail) if content_detail else []
                df2 = pd.DataFrame(content_detail, dtype=object)
                df = pd.merge(df1, df2, left_on='content_id', right_on='content_id', how='left')
                content_ids = df[~df['parent_id'].isnull()]['parent_id'].tolist()
                return  content_ids
            except Exception as e:
                LOGGER.error('error in watched tv shows {}'.format(e))
                return []



class ContentViewSet(viewsets.ViewSet,CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)


    @classmethod
    def  get(cls,content_list):
            results = []
            for content_id in content_list:
                content=filter_by_key(Content,content_id=content_id)
                if content:
                    results =results+list(content)
                else :
                    results.append({"content_id":content_id,"content_name":"NA","content_type":"NA","language":"NA","mou":"0",})
            serializer_class = ContentSerializer(data=results,many=True)
            serializer_class.is_valid()
            code = 200 if serializer_class.data else 204
            results=Results(code,"SUCCESS",extra_field={"results":serializer_class.data}).serialize()
            return Response(results,status=status.HTTP_200_OK)


    def content_publish(self, request, *args, **kwargs):
        import xml.etree.ElementTree as et

        # xml_path=request.data['file']
        tree = et.parse(request)

        root = tree.getroot()

        xmlns =root.tag[:root.tag.rindex('}') + 1]
        content_publish = {}

        for elem in tree.iter(tag=xmlns+'content'):
            for child in elem:
                if child.tag == xmlns+'contentId':
                    content_publish.update({'content_id': child.text})
                elif child.tag == xmlns+'contentName':
                    content_publish.update({'content_name': child.text})
                elif child.tag == xmlns+'contentType':
                    content_publish.update({'content_type': child.text})

                elif child.tag == xmlns+'properties':
                    for c in child:
                        if c.attrib['name'] == 'language':
                            content_publish.update({'language': [i.attrib['value'] for i in c]})
                        elif c.attrib['name'] == 'duration':
                            content_publish.update({c.attrib['name']: c.attrib['value']})
                        elif c.attrib['name'] == 'Genre':
                            content_publish.update({'genre': [i.attrib['value'] for i in c]})
                        elif c.attrib['name'] == 'Person':
                            content_publish.update(
                                {'actor': [i.attrib['value'] for i in c if i.attrib['name'] == 'Actor']})

        # print(content_publish)
        file_serializer = ContentWriteSerializer(data=content_publish)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def content_unpublish(self,request,content_id):
        try:
            content = Content.objects.get(content_id=content_id)
        except Content.DoesNotExist:
            results = Results(400, "FAIL", "unable to process your request right now.").serialize()
            return Response(results, status=status.HTTP_400_BAD_REQUEST)

        content.delete()
        results = Results(200, "SUCCESS", "content deleted").serialize()
        return Response(results, status=status.HTTP_200_OK)



class RecommendationViewSet(viewsets.ViewSet):

    def delete(self,request,**kwargs):
        recomm = RecommendationSerializer(data=request.data)
        if recomm.is_valid():
            no ,_ =recomm.delete()
            return Response(Results(200, "SUCCESS",str(no)+" contents are deleted.").serialize(), status=status.HTTP_200_OK)
        return Response(recomm.errors, status=status.HTTP_400_BAD_REQUEST)



























