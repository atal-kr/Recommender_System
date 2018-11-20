from django.conf.urls import url, include
from django.views.generic import TemplateView

from applications.common.url_map import NOTIFICATION_UPDATE, SEND_NOTIFICATION, NOTIFICATION_HISTORY, FETCH_SUMMARY

notification_url =[
    url(r'^$',TemplateView.as_view(template_name='recommendation/Login.html')),

    url(r'view_recommendation/$', TemplateView.as_view(template_name='recommendation/view_recommended_notification.html'),name='view_recommendation'),
    url(r'send_notification/$',
        TemplateView.as_view(template_name='recommendation/send_notification.html'),name='send_notification'),
    url(r'view_summary/$',
        TemplateView.as_view(template_name='recommendation/view_summary.html'),name="view_summary"),
    url(r'update/$',NOTIFICATION_UPDATE,name='update'),
    url('send/$',SEND_NOTIFICATION,name='send'),
    url(r'view/$',NOTIFICATION_HISTORY,name='view'),
    url(r'summary/$',FETCH_SUMMARY,name='summary')
]