from django.conf.urls import url
from django.views.generic import TemplateView
from applications.recommendation.rec_ui import test
from applications.common.url_map import GET_USER, UPDATE_USER, STREAM_HISTORY_UPDATE, GET_RECOMMENDATION, \
    GET_CONTENT_SEEN, DELETE_RECOMM, USER_ACTION, CONTENT_PUBLISH, CONTENT_UNPUBLISH

urlpatterns=[
    url(r'test/',TemplateView.as_view(template_name='recommendation/recomm.html') ,name='test'),
    url(r'user/(?P<user_id>[\w\s]+)$',GET_USER),
    url(r'stream_history/(?P<user_id>[\w\s]+)$',GET_CONTENT_SEEN),

    url(r'v1/list/(?P<user_id>[\w\s]+)/(?P<recommendation_bucket>[\w\s]+)$',GET_RECOMMENDATION),
    url(r'v1/list/(?P<user_id>[\w\s]+)/(?P<recommendation_bucket>[\w\s]+)/(?P<content_id>[\w\s]+)',GET_RECOMMENDATION),
    url(r'render/',test,name="render"),

    url(r'delete/$',DELETE_RECOMM),
    url(r'user/action/',USER_ACTION),

    url(r'content/publish/$', CONTENT_PUBLISH),
    url(r'content/unpublish/(?P<content_id>[\w]+)$', CONTENT_UNPUBLISH)

]
user_url= [
    url(r'stream_history/update/$',STREAM_HISTORY_UPDATE),
    url(r'update/$',UPDATE_USER),
]