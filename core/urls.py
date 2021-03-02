from django.urls import path, include, re_path

from .views import *

urlpatterns = [
    path('create/', ProjectCreateView.as_view()),
    path('schema/<pid>/', SchemaView.as_view()),
    path('info/<pid>/', ProjectInfoView.as_view()),
    path('list/<uname>/', UserProjectListView.as_view()),
    path('code/download/<pid>/', CodeDownloadView.as_view()),
    re_path(r'code/(?P<pid>[1-9]+)/(?P<path>.*)/$', CodeView.as_view(), name="file_path"),
    path('custom_message/<int:id>/', CustomMessageFieldView.as_view()),
    path('custom_message/list/', CustomMessageFieldListView.as_view()),
    path('build/', BuildUnitView.as_view()),    
]
