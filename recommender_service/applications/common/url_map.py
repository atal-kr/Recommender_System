from applications.notification.dashboard import Notification_Dashborad
from applications.recommendation.controler import RecommendationController
from applications.common.lib import LoginView, LogoutView
from applications.recommendation.views import UserViewSet, ContentSeenViewSet, ContentViewSet, RecommendationViewSet

GET_USER = UserViewSet.as_view(actions={'get':'get'})
UPDATE_USER = UserViewSet.as_view(actions={'post':'post'})
STREAM_HISTORY_UPDATE = ContentSeenViewSet.as_view(actions={'post':'post'})
GET_CONTENT_SEEN = ContentSeenViewSet.as_view(actions={'get':'get'})
UPDATE_CONTENT = ContentViewSet.as_view(actions={'post':'post'})
GET_RECOMMENDATION = RecommendationController.as_view(actions={'get':"get"})
SIMILAR_CONTENT = RecommendationController.as_view(actions={"get":"similar_content"})
LOG_IN = LoginView.as_view()
LOG_OUT =LogoutView.as_view()
NOTIFICATION_UPDATE = Notification_Dashborad.as_view(actions={'post':'update'})
SEND_NOTIFICATION = Notification_Dashborad.as_view(actions={'post':'send'})
NOTIFICATION_HISTORY = Notification_Dashborad.as_view(actions={'post':'view_notification'})
FETCH_SUMMARY = Notification_Dashborad.as_view(actions={'post':'fetch_summary'})

DELETE_RECOMM = RecommendationViewSet.as_view(actions={'post':'delete'})

USER_ACTION = UserViewSet.as_view(actions={'post':'perform_action'})

CONTENT_PUBLISH = ContentViewSet.as_view(actions={'post':'content_publish'})

CONTENT_UNPUBLISH = ContentViewSet.as_view(actions={'post':'content_unpublish'})

