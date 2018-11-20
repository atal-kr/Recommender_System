from django.http import JsonResponse
from django.shortcuts import render
from recommender_service.settings import BASE_DIR
import json
from applications import VERSION
with open(BASE_DIR+"/conf/swagger.json") as json_data:
    json_data=json.load(json_data)
    json_data['info']['version'] = VERSION

def swagger_json(request):
    response=JsonResponse(json_data)
    #response['Access-Control-Allow-Origin']='*'
    return response

def swagger_ui(request):
    return render(request,'swagger/index.html')