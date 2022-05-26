import subprocess
import os
import yaml
from fastapi import FastAPI
from fastapi.testclient import TestClient
from StorySquadAI.WebApi import app
import requests

test_client = TestClient(app.app)


def read_procfile(path: str):
    """
    Reads a Procfile and returns a dictionary of process name to command
    :param path:    the path to the Procfile
    :return:        a dictionary of process name to command
    """
    if os.path.exists(path):
        proc = open(os.path.join(path, "Procfile"), "r")
        proc_contents = yaml.load(proc, yaml.Loader)
        proc.close()
        return proc_contents
    else:
        print("Procfile not found")


def find_file_in_parent_dirs(filename: str, path: str, depth: int) -> str:
    """
    Find a file recursively in parent directories
    :param filename:     Name of file to find
    :param path:         Path to search in
    :param depth:        Depth of recursion
    :return:             Full path name of file if found, -1 otherwise
    """
    search_path = os.path.normpath(path)
    for i in range(depth):
        if os.path.exists(os.path.join(search_path, filename)):
            return os.path.normpath(search_path)
        search_path = os.path.join(search_path, "..")
    return -1


def test_heroku_deployment_should_serve():
    procfile_dir = find_file_in_parent_dirs("Procfile", ".", 10)
    assert procfile_dir != -1
    web_command = read_procfile(procfile_dir)["web"]
    assert uvicorn_tester( web_command,port ="8080", app_name="app") == 0


def test_setup():
    response = test_client.get("/")
    assert response.status_code == 200


def uvicorn_tester(uvicorn_command,port="8080", app_name="app"):
    uvicorn_command = uvicorn_command.replace("$PORT", port)
    print("\nExecuting command: " + uvicorn_command + "\n")
    try:
        proc_uvicorn = subprocess.Popen(uvicorn_command)
        print("\nUvicorn command has executed successfully.\n")
        try:
            # responds when the server is up
            response = requests.get("http://127.0.0.1:" + str(port))
            print("\nSuccessful response from server.\n")
            print("\nkilling server.\n")
            proc_uvicorn.kill()
            return 0
        except:
            print("\nServer is not responding.\n")
            print("\nkilling server.\n")
            proc_uvicorn.kill()
            return 1
    except subprocess.CalledProcessError as e:
        print("\nError calling uvicorn server.\n")
        print(str(e.output))
        return e.returncode
