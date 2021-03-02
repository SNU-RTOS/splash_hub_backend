from django.db import models
from django.utils.translation import ugettext_lazy as _

from authorization.models import User

class Project(models.Model):
    author = models.ForeignKey(User, related_name="project", on_delete=models.SET_NULL, null=True)
    wrote_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=500)
    schema = models.TextField(null=True, blank=True)
    
class Code(models.Model):
    project = models.ForeignKey(Project, related_name="code", on_delete=models.CASCADE)
    path = models.CharField(max_length=255)

class CustomMessage(models.Model):
    user = models.ForeignKey(User, related_name="custom_messages", on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now_add=True)

class MessageField(models.Model):
    message = models.ForeignKey(CustomMessage, related_name='fields', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    PACKAGE_CHOICES = (
		('std_msgs', 'std_msgs'),
        ('sensor_msgs', 'sensor_msgs'),
        ('geometry_msgs', 'geometry_msgs'),
        ('nav_msgs', 'nav_msgs'),
        ('shape_msgs', 'shape_msgs'),
        ('stereo_msgs', 'stereo_msgs'),
        ('trajectory_msgs', 'trajectory_msgs'), 
        ('visualization_msgs', 'visualization_msgs'),
        ('custom_msgs', 'custom_msgs')
    )
    package = models.CharField(max_length=30, choices=PACKAGE_CHOICES)
    field_type = models.CharField(max_length=30)

class BuildUnit(models.Model):
    project = models.ForeignKey(Project, related_name="build_units", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)