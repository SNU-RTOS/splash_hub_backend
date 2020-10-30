from django.urls import path, include, re_path

from .views import *

urlpatterns = [
    path('create/', ProjectCreate.as_view()),
    path('schema/<pid>/', Schema.as_view()),
    path('info/<pid>/', ProjectInfo.as_view()),
    path('list/<uname>/', UserProjectList.as_view()),
    re_path(r'code/(?P<pid>[1-9]+)/(?P<path>.*)/$', Code.as_view(), name="file_path"),

]
