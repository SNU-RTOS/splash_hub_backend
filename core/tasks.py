from django.utils import timezone
from django.conf import settings

import subprocess
import os
import asyncio
import json

path = "/Users/yehyun/Desktop/Splash/splash_code_generator"
async def save_code(username, title, prev_schema, schema):
    try:
        if os.path.isdir("usr_src/{}/src/{}".format(username, title)) :
            merge_code(username, title, prev_schema, schema)
            return
        if not os.path.isdir("usr_src/{}".format(username)):
            os.makedirs("usr_src/{}".format(username))
        if not os.path.isdir("usr_src/{}/src".format(username)):
            os.makedirs("usr_src/{}/src".format(username))
        with open("usr_src/{}/temp.json".format(username), "w") as f:
            f.write(schema)
        command = "python {}/main.py --name {} --file temp.json --path {}/usr_src/{}".format(path, title, settings.BASE_DIR, username)
        process = subprocess.Popen(command.split(), cwd="usr_src/{}".format(username), stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = process.communicate()
        print(out)
        print(err)
    except Exception as e:
        print("error occurs while save code: ", str(e))
    finally:
        if os.path.isfile("usr_src/{}/temp.json".format(username)):
            os.remove("usr_src/{}/temp.json".format(username))


def merge_code(username, title, prev_schema, schema):
    prev_schema = json.loads(prev_schema)
    schema = json.loads(schema)
    added, removed, modified = compare_schema(prev_schema, schema)
    print("Added: ", added)
    print("removed: ", removed)
    print("modified: ", modified)

def compare_schema(prev, new):

    prev_length = len(prev["nodeDataArray"])
    new_length = len(new["nodeDataArray"])
    prev_uuid = [0]*prev_length
    new_uuid = [0]*new_length

    for i in range(prev_length):
        prev_uuid[i]= prev["nodeDataArray"][i]["UUID"]

    new_length = len(new["nodeDataArray"])
    for i in range (new_length):
        new_uuid[i] = new["nodeDataArray"][i]["UUID"]

    set_prevuuid = set(prev_uuid)
    set_newuuid = set(new_uuid)
    shared = set_prevuuid.intersection(set_newuuid)
    shared_list = list(shared)

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
        #print("Added: none")
        added_list2 = []
    else:
        for i in range(len(added_list)):
            added_list2[i] = new["nodeDataArray"][new_uuid.index(added_list[i])]
        #print("Added: ", *added_list2, sep = '\n')

    if removed_list == ["none"]:
        #print("Removed: none")
        removed_list2 = []
    else:
        for i in range(len(removed_list)):
            removed_list2[i] = prev["nodeDataArray"][prev_uuid.index(removed_list[i])]
        #print("Removed: ", *removed_list2, sep = '\n')

    modified_dict = {"Modified: ": [0]*len(modified_list)}

    if modified_list == ["none"]:
        #print("Modified: none")
        modified_dict = []

    else:
        for i in range(len(modified_list)):
            set1 = set(prev["nodeDataArray"][prev_uuid.index(modified_list[i])].items())
            set2 = set(new["nodeDataArray"][new_uuid.index(modified_list[i])].items())
            diction1 = {"UUID: ": prev["nodeDataArray"][i]["UUID"]}
            diction1["from"] = set1-set2
            diction1["to"] = set2-set1
            modified_dict["Modified: "][i] = diction1

    #print(modified_dict)
    return added_list2, removed_list2, modified_dict

    