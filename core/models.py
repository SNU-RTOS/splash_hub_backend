from django.db import models
from django.utils.translation import ugettext_lazy as _

from authorization.models import User

class Project(models.Model):
    author = models.ForeignKey(User, related_name="project", on_delete=models.SET_NULL, null=True)
    wrote_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=500)
    schema = models.CharField(max_length=10000, null=True, blank=True)

class Code(models.Model):
    project = models.ForeignKey(Project, related_name="code", on_delete=models.CASCADE)
    path = models.CharField(max_length=255)