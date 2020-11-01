from django.shortcuts import render

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Project, Code
from .serializers import ProjectSerializer, ProjectListSerializer
from authorization.models import User
from datetime import datetime
import asyncio
import os
from .tasks import save_code
class ProjectCreate(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            author = request.user
            name = request.data['name']
            description = request.data['description']
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

class Schema(APIView):
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
            project.schema = data
            project.edited_on = datetime.now()
            project.save()
            asyncio.run(save_code(user.username, project.name, data))
            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))

class ProjectInfo(APIView):
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

class UserProjectList(APIView):
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

class Code(APIView):
    permission_classes=[AllowAny]
    def get(self, request, *args, **kwargs):
        try:
            project_id = kwargs['pid']
            file_path = kwargs['path']
            project = Project.objects.get(id=project_id)
            username = project.author.username

            if not os.path.isdir("usr_src/{}/src/{}".format(username, project.name)) :
                return Response(status=status.HTTP_404_BAD_REQUEST, data="No such project's file")
            
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