from django.utils import timezone
from django.conf import settings

import subprocess
import os
import asyncio

path = "/Users/hwancheolkang/Workspace/rtos/Splash/splash_code_generator"
async def save_code(username, title, schema):
    try:
        if os.path.isdir("usr_src/{}/src/{}".format(username, title)) :
            merge_code(username, title, schema)
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
    except Exception:
        pass
    finally:
        if os.path.isfile("usr_src/{}/temp.json".format(username)):
            os.remove("usr_src/{}/temp.json".format(username))


def merge_code(username, title, schema):
    pass