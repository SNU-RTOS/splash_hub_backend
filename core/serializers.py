from rest_framework.serializers import ModelSerializer, SerializerMethodField

from django.contrib.auth import get_user_model

from .models import *
from authorization.serializers import UserSerializer
import os
from datetime import datetime
class ProjectSerializer(ModelSerializer):
    author_info = UserSerializer(source='author', read_only=True)
    code_tree = SerializerMethodField('get_code_tree')
    def get_code_tree(self, project):
        return self.path_to_dict('./usr_src/{}/src/{}'.format(project.author.username, project.name))
    def path_to_dict(self, path):
        d = {'name': os.path.basename(path), 'last_modified': datetime.fromtimestamp(os.path.getmtime(path))}
        if os.path.isdir(path):
            d['type'] = "directory"
            d['children'] = [self.path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
        else:
            d['type'] = "file"
        return d
    class Meta:
        model = Project
        fields = ['author_info', 'name', 'description', 'wrote_on', 'edited_on', 'schema', 'code_tree']

class ProjectListSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'wrote_on', 'edited_on']

class MessageFieldSerializer(ModelSerializer):
    class Meta:
        model = MessageField
        fields = '__all__'

class CustomMessageFieldSerializer(ModelSerializer):
    fields = MessageFieldSerializer(many=True, read_only=True)
    class Meta:
        model = CustomMessage
        fields = '__all__'

class BuildUnitSerializer(ModelSerializer):
    class Meta:
        model = BuildUnit
        fields = '__all__'