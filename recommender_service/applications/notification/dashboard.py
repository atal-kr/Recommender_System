from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from rest_framework import viewsets


from applications.common.constant import REC_MAXLIMIT
from applications.notification.models import Notification_History, Recommended_Notification
from applications.common.lib import filter_by_key
from applications.notification.tasks import update_notification, send_notification, update_and_send
from applications.notification.utils import NotificationUtils


class Notification_Dashborad(viewsets.ViewSet):
    def send(self,request,*args,**kwargs):
        from_csv = False
        if request.method == 'POST' :
            bucket = request.POST.get('bucket')
            myfile = request.FILES.get('csv_file')
            if bucket== 'from_csv'and myfile:
                from_csv =True
                fs = FileSystemStorage()
                fs.delete(myfile.name)
                fs.save('user_list.csv', myfile)
            user_list = NotificationUtils.user_list_for_notification(from_csv=from_csv)
            length = len(user_list)
            for i in range(10):
                users = user_list[int((i*0.1)*length):int(((i+1)*0.1)*length)]
                if users:
                    if from_csv :
                        update_and_send.delay(users)
                    else:
                        send_notification.delay(users)
        return render(request,'recommendation/send_notification.html',{'message':"notification sent."})


    def update(self,request,**kwargs):
        user_list = NotificationUtils.user_list_for_notification()
        length = len(user_list)
        for i in range(10):
            users = user_list[int((i * 0.1) * length):int(((i + 1) * 0.1) * length)]
            if users:
                update_notification.delay(users)
        return render(request, 'recommendation/send_notification.html', {'message': "updated..."})


    def view_notification(self,request):
        user_id = request.POST.get('user_id')
        print(user_id)
        queryset = filter_by_key(Notification_History,user_id=user_id).order_by('-modified')[:REC_MAXLIMIT]
        results = list(queryset.values('user_id','content_id','created','modified'))
        return render(request,'recommendation/view_recommended_notification.html',{'results':results})

    def fetch_summary(self,request):
        queryset = filter_by_key(Recommended_Notification)
        distinct_content = queryset.values_list('content_id', flat=True).distinct()
        user_count = queryset.count()
        content_count = distinct_content.count()
        distinct_content = list(distinct_content) if distinct_content else []
        results = {
                    'user_count':user_count,
                    'content_count':content_count,
                    'distinct_content':distinct_content
                }
        return render(request,'recommendation/view_summary.html',{'results':results})


