from django.contrib import admin

from authorization.models import User

admin.site.register(User)  # 유저 정보 어드민 사이트에서 볼 수 있게 추가

 