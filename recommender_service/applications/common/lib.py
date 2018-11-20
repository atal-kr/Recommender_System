from django.contrib.auth import login, logout
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.common.response import Results
from applications.recommendation.serializer import LoginSerializer
from rest_framework.authtoken.models import Token

def filter_by_key(model,**key):
    try:
        queryset =model.objects.filter(**key)
    except Exception:
        queryset = model.objects.none()
    return queryset

def get_by_key(model,**key):
    try:
        queryset = model.objects.get(**key)
    except Exception:
        queryset = model.objects.none()
    return queryset

def parse_request(request):
    results= {}
    return results



class LoginView(APIView):
    exclude_from_schema = True
    def post(self,request,*args,**kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        login (request,user)
        token ,created=Token.objects.get_or_create(user=user)
        return Response({"Token":token.key},status=status.HTTP_200_OK)
        #return render(request,'recommendation/recomm.html',{"Token":token.key})

class LogoutView(APIView):
    exclude_from_schema = True
    authentication_classes = (TokenAuthentication,)

    def post(self,request,*args,**kwargs):
        logout(request)
        return Response({})