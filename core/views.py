from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny

from .models import Project, Code
from .serializers import *
from authorization.models import User
from datetime import datetime
import asyncio
import zipfile

import os, json

from .tasks import save_code, delete_code, build_docker_image

class ProjectCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            author = request.user
            name = request.data['name']
            description = request.data['description']
            description = description.replace('\n', '\\n')
            try:
                check = Project.objects.get(author=author, name=name)
            except Project.DoesNotExist:
                check = None
            
            if check:
                return Response(status=status.HTTP_226_IM_USED)
            project = Project(author=author, name=name, description=description)
            project.schema = '{ "class": "GraphLinksModel",  "linkKeyProperty": "key",  "nodeDataArray": [],  "linkDataArray": []}'
            project.save()
            return Response(status=status.HTTP_201_CREATED, data={'project_id': project.id})
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_400_BAD_REQUEST)

class SchemaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            project_id = kwargs['pid']
            project = user.project.filter(pk=project_id).first()
            return Response(status=status.HTTP_200_OK, data={'schema': project.schema})
        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))

    def put(self, request, *args, **kwargs):
        user = request.user
        try:
            project_id = kwargs['pid']
            data = request.data['data']
            
            project = user.project.filter(pk=project_id).first()
            prev_schema = project.schema
            project.schema = data
            project.edited_on = datetime.now()
            project.save()
            asyncio.run(save_code(user, project.name, prev_schema, data))
            asyncio.run(build_docker_image(user, project.name))
            
            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))

class ProjectInfoView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            project_id = kwargs['pid']
            project_obj = Project.objects.get(id=project_id)
            serializer = ProjectSerializer(project_obj, many=False)
            data = serializer.data
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class UserProjectListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            username = kwargs['uname']
            user = User.objects.get(username=username)
            projects = user.project
            serializer = ProjectListSerializer(projects, many=True)
            data = serializer.data
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class CodeView(APIView):
    permission_classes=[AllowAny]
    def get(self, request, *args, **kwargs):
        try:
            project_id = kwargs['pid']
            file_path = kwargs['path']
            project = Project.objects.get(id=project_id)
            username = project.author.username

            if not os.path.isdir("usr_src/{}/src/{}".format(username, project.name)) :
                return Response(status=status.HTTP_404_NOT_FOUND, data="No such project's file")
            
            file_path = file_path.replace('(', '').replace(')', '')
            file_path = file_path.split('/')
            root_path = "usr_src/{}/src/{}".format(username, project.name)
            cur_path = root_path
            for path in file_path:
                cur_path = '{}/{}'.format(cur_path, path)
            
            file_str = ''
            with open(cur_path, 'r') as f:
                file_str = f.read()
            return Response(status=status.HTTP_200_OK, data=file_str)
        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        try:
            project_id = kwargs['pid']
            file_path = kwargs['path']
            project = Project.objects.get(id=project_id)
            username = project.author.username
            
            file_path = file_path.replace('(', '').replace(')', '')
            file_path = file_path.split('/')
            root_path = f"usr_src/{username}/src/{project.name}"
            cur_path = root_path
            for path in file_path:
                cur_path = f'{cur_path}/{path}'
            
            file_str = request.data['code']   
            with open(cur_path, 'w') as f:
                f.write(file_str)
            return Response(status=status.HTTP_200_OK, data=file_str)
        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))


class CodeDownloadView(APIView):
    permission_classes=[AllowAny]
    def get(self, request, *args, **kwargs):
        try:
            prev_dir = os.getcwd()
            project_id = kwargs['pid']
            project = Project.objects.get(id=project_id)
            username = project.author.username

            if not os.path.isdir("usr_src/{}/src/{}".format(username, project.name)) :
                return Response(status=status.HTTP_404_BAD_REQUEST, data="No such project's file")
            os.chdir("usr_src/{}/src".format(username))
            response = HttpResponse(content_type='application/zip')
            zf = zipfile.ZipFile(response, 'w')
            for root, dirs, files in os.walk(project.name):
                for file in files:
                    zf.write(os.path.join(root, file))
            
            response['Content-Disposition'] = f'attachment; filename={project.name}'
            return response
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
        finally:
            os.chdir(prev_dir)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class CustomMessageFieldView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            message_id = kwargs.get('id')
            message = CustomMessage.objects.get(id=message_id)
            serializer = CustomMessageFieldSerializer(message, many=False)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))

    def put(self, request, *args, **kwargs):
        try:
            user = request.user
            fields_from_request = json.loads(request.data['fields'])
            name = request.data['name']
            try:
                message_id = kwargs.get('id')
                message = CustomMessage.objects.get(id=message_id)
                message.name = name
            except Exception:
                message = CustomMessage(user=user, name=name)
            message.save()
            message.fields.all().delete()
                
            for field in fields_from_request:
                MessageField(message=message, name=field['name'], package=field['package'], field_type=field['field_type']).save()

            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))



class CustomMessageFieldListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            custom_messages = user.custom_messages.all()
            serializer = CustomMessageFieldSerializer(custom_messages, many=True, read_only=True)

            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))

class BuildUnitView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            project_id = kwargs.get('pid')
            project = Project.objects.get(id=project_id)
            build_units = project.build_units.all()
            serializer = BuildUnitSerializer(build_units, many=True)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            project_id = kwargs.get('pid')
            project = Project.objects.get(id=project_id)
            schema_data = project.schema
            
            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response(stauts=status.HTTP_400_BAD_REQUEST, data=str(e))
