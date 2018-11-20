"""recommender_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin


from applications.notification.urls import notification_url
from applications.recommendation.urls import urlpatterns, user_url
from recommender_service.swagger import swagger_json, swagger_ui
from django.conf.urls.static import static

from applications.common.url_map import LOG_IN, LOG_OUT

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^swagger.json/$', swagger_json),
     url(r'login/',LOG_IN,name='login'),
    url(r'recommendation/', include(urlpatterns, namespace="recommendation")),
    url(r'recommendation/notification/',include(notification_url, namespace='notification')),
    url(r'apidocs/$',swagger_ui),
    url(r'logout/',LOG_OUT,name='logout'),
    url(r'user/',include(user_url,namespace="user")),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)