from django.utils import timezone
from django.conf import settings

import subprocess
import os
import asyncio
import json
from .models import Project
import docker

path = settings.SPLASH_CODE_GENERATOR_PATH
client = docker.from_env()
docker_api = client.api
docker_image = client.images
docker_container = client.containers
async def save_code(user, title, prev_schema, schema):
    try:
        if os.path.isdir("usr_src/{}/src/{}".format(user.username, title)) :
            merge_code(user.username, title, prev_schema, schema)
        else:
            generate_code(user, title, schema)
            
    except Exception as e:
        print("error occurs while save code: ", str(e))
        raise e
    finally:
        if os.path.isfile("usr_src/{}/temp.json".format(user.username)):
            os.remove("usr_src/{}/temp.json".format(user.username))

def generate_code(user, title, schema):
    if not os.path.isdir("usr_src/{}/src".format(user.username)):
        os.makedirs("usr_src/{}/src".format(user.username))
    with open("usr_src/{}/temp.json".format(user.username), "w") as f:
        f.write(schema)
    command = "python {}/main.py --name {} --file temp.json --path {}/usr_src/{} --username {} --email {}".format(path, title, settings.BASE_DIR, user.username, user.username, user.email)
    # print(command)
    process = subprocess.Popen(command.split(), cwd="usr_src/{}".format(user.username), stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = process.communicate()
    # print(out)
    print(err)
    if err:
        delete_code(user, title)
        project = Project.objects.get(title=title)
        project.delete()
def merge_code(user, title, prev_schema, schema):
    prev_schema = json.loads(prev_schema)
    schema = json.loads(schema)
    added_nodes, removed_nodes, modified_nodes = compare_schema_node(prev_schema, schema)
    added_links, removed_links, modified_links = compare_schema_link(prev_schema, schema)
    base_dict = {'class': 'GraphLinksModel', 'linkKeyProperty': 'key', 'nodeDataArray': [], 'linkDataArray': []}
    added_dict = removed_dict = modified_dict = base_dict
    
    added_dict["nodeDataArray"] =  added_nodes
    removed_dict["nodeDataArray"] = removed_nodes
    
    print("Added nodes: ", added_nodes)
    print("Removed nodes: ", removed_nodes)
    print("Modified nodes: ", modified_nodes)
    print("Added links: ", added_links)
    print("Removed links: ", removed_links)
    print("Modified links: ", modified_links)

def compare_schema_node(prev, new):
    prev_length = len(prev["nodeDataArray"])
    new_length = len(new["nodeDataArray"])
    prev_uuid = [0]*prev_length
    new_uuid = [0]*new_length

    for i in range(prev_length):
        prev_uuid[i]= prev["nodeDataArray"][i]["UUID"]

    for i in range (new_length):
        new_uuid[i] = new["nodeDataArray"][i]["UUID"]

    set_prevuuid = set(prev_uuid)
    set_newuuid = set(new_uuid)
    shared = set_prevuuid.intersection(set_newuuid)

    removed = set_prevuuid-set_newuuid
    if removed ==set():
        removed = {"none"}
    added = set_newuuid-set_prevuuid
    if added == set():
        added = {"none"}

    same = set(a for a in shared if prev["nodeDataArray"][prev_uuid.index(a)] == new["nodeDataArray"][new_uuid.index(a)])
    modified = set(a for a in shared if prev["nodeDataArray"][prev_uuid.index(a)] != new["nodeDataArray"][new_uuid.index(a)])

    if modified ==set():
        modified = {"none"}

    added_list = list(added)
    removed_list = list(removed)
    modified_list = list(modified)

    added_list2 = [0]*len(added_list)
    removed_list2 = [0]*len(removed_list)
    modified_list2 = [0]*len(modified_list)
    modified_list3 = [0]*len(modified_list)

    if added_list == ["none"]:
        added_list2 = []
    else:
        for i in range(len(added_list)):
            added_list2[i] = new["nodeDataArray"][new_uuid.index(added_list[i])]

    if removed_list == ["none"]:
        removed_list2 = []
    else:
        for i in range(len(removed_list)):
            removed_list2[i] = prev["nodeDataArray"][prev_uuid.index(removed_list[i])]

    modified_list2 = []

    if modified_list == ["none"]:
        modified_list2 = []

    else:
        for i in range(len(modified_list)):
            set1 = set(prev["nodeDataArray"][prev_uuid.index(modified_list[i])].items())
            set2 = set(new["nodeDataArray"][new_uuid.index(modified_list[i])].items())
            diction1 = {"UUID: ": prev["nodeDataArray"][i]["UUID"]}
            diction1["from"] = set1-set2
            diction1["to"] = set2-set1
            modified_list2.append(diction1)

    return added_list2, removed_list2, modified_list2

def compare_schema_link(prev, new):
    prev_length = len(prev["linkDataArray"])
    new_length = len(new["linkDataArray"])
    prev_key = [0]*prev_length
    new_key = [0]*new_length

    for i in range(prev_length):
        prev_key[i]= prev["linkDataArray"][i]["key"]

    for i in range (new_length):
        new_key[i] = new["linkDataArray"][i]["key"]

    print("prev_key", prev_key)
    print(new_key)
    set_prevkey = set(prev_key)
    set_newkey = set(new_key)
    shared = set_prevkey.intersection(set_newkey)


    removed = set_prevkey-set_newkey
    if removed ==set():
        removed = {"none"}

    added = set_newkey-set_prevkey
    if added == set():
        added = {"none"}

    modified = set(a for a in shared if prev["linkDataArray"][prev_key.index(a)] != new["linkDataArray"][new_key.index(a)])

    if modified ==set():
        modified = {"none"}

    added_list = list(added)
    removed_list = list(removed)
    modified_list = list(modified)
    print(added_list, removed_list, modified_list)


    added_list2 = [0]*len(added_list)
    removed_list2 = [0]*len(removed_list)
    modified_list2 = [0]*len(modified_list)
    modified_list3 = [0]*len(modified_list)

    if added_list == ["none"]:
        added_list2 = []
    else:
        for i in range(len(added_list)):
            added_list2[i] = new["linkDataArray"][new_key.index(added_list[i])]

    if removed_list == ["none"]:
        removed_list2 = []
    else:
        for i in range(len(removed_list)):
            removed_list2[i] = prev["linkDataArray"][prev_key.index(removed_list[i])]

    modified_list2 = []

    if modified_list == ["none"]:
        modified_list2 = []

    else:
        for i in range(len(modified_list)):
            set1 = set(prev["linkDataArray"][prev_key.index(modified_list[i])].items())
            set2 = set(new["linkDataArray"][new_key.index(modified_list[i])].items())
            diction1 = {"key: ": prev["linkDataArray"][i]["key"]}
            diction1["from"] = set1-set2
            diction1["to"] = set2-set1
            modified_list2.append(diction1)

    return added_list2, removed_list2, modified_list2

def delete_code(user, title):
    os.rmdir("usr_src/{}/src/{}".format(user.username, title))

async def build_docker_image(user, title):
    path = f'usr_src/{user.username}/src/Dockerfile'
    username = user.username.lower()
    with open(path, 'w') as f:
        f.write('FROM splash_environment:0.0\n')
        # f.write(f'COPY {title} /root/dev_ws/src/{title}\n')
        f.write('WORKDIR /root/dev_ws\n')
        f.write('SHELL ["/bin/bash", "-c"]\n')
        f.write('RUN echo \"source /opt/ros/dashing/setup.bash\" >> /root/.bashrc\n')
        # f.write('RUN colcon build\n')
        # f.write('RUN echo \"source /root/dev_ws/install/setup.bash\" >> /root/.bashrc\n')
        f.write('RUN apt update\n')
        f.write('RUN apt install -y openssh-server\n')
        f.write('RUN mkdir /var/run/sshd\n')
        f.write('RUN echo \'root:root\' | chpasswd\n')
        f.write('RUN sed -ri \'s/^#?PermitRootLogin\s+.*/PermitRootLogin yes/\' /etc/ssh/sshd_config\n')
        f.write('RUN sed -ri \'s/UsePAM yes/#UsePAM yes/g\' /etc/ssh/sshd_config\n')
        f.write('RUN mkdir /root/.ssh\n')
        f.write('RUN echo \"cd /root/dev_ws\" >> /root/.bashrc\n')
        f.write('RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*\n')
        f.write('EXPOSE 22\n')
        f.write('CMD [\"/usr/sbin/sshd\", \"-D\"]\n')

    image = docker_image.build(path=f'{settings.BASE_DIR}/usr_src/{user.username}/src', tag=f'{username}_splash_{title}:0.0')
    docker_container.run(image=f'{username}_splash_{title}:0.0', init=True, tty=True, detach=True, name=f'{username}_splash_{title}', ports={'22/tcp': 11111}, volumes={f'{settings.BASE_DIR}/usr_src/{user.username}/src/{title}': {'bind': f'/root/dev_ws/src/{title}', 'mode': 'rw'}})
    os.remove(path)


async def make_build_unit(user, title, build_unit_name):
    path = f'usr_src/{user.username}/src/Dockerfile'
    username = user.username.lower()
    with open(path, 'w') as f:
        f.write(f'FROM {username}_splash_{title}:0.0\n')
        f.write('WORKDIR /root/dev_ws\n')
        f.write('SHELL ["/bin/bash", "-c"]\n')
        f.write('RUN echo \"source /opt/ros/dashing/setup.bash\" >> /root/.bashrc\n')
        f.write(f'COPY {title} /root/dev/src/{title}\n')
        f.write('colcon build')
        f.write('RUN echo \"source /root/dev_ws/install/setup.bash\" >> /root/.bashrc\n')
        f.write('CMD ros2 run {title} {build_unit_name}')

    image = docker_image.build(path=f'{settings.BASE_DIR}/usr_src/{user.username}/src', tag=f'{username}_splash_{title}_{build_unit_name}:0.0')
    docker_container.run(image=f'{username}_splash_{title}_{build_unit_name}:0.0', init=True, tty=True, detach=True, name=f'{username}_splash_{title}_{build_unit_name}')
    os.remove(path)