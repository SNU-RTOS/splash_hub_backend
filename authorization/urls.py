from django.urls import path, include

from .views import *

urlpatterns = [
    path('user/info/', UserInfo.as_view()),
    path('check_duplication/username/', UsernameDuplicationCheck.as_view()),
    path('check_duplication/email/', EmailDuplicationCheck.as_view()),
    path('rest_auth/', include('rest_auth.urls')),
    path('rest_auth/registration/', include('rest_auth.registration.urls'))
]
