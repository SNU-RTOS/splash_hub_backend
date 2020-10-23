from django.urls import path, include

from .views import *

urlpatterns = [
    path('create/', ProjectCreate.as_view()),
    path('schema/<pid>/', Schema.as_view()),
    path('info/<pid>/', ProjectInfo.as_view()),
    path('list/<uname>/', UserProjectList.as_view()),

]
