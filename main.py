import os
import webbrowser
from pathlib import Path
import json
from datetime import datetime
from dateutil.parser import parse
import configparser
import requests
import hashlib
import os
import sys
from rauth import OAuth2Service
from tqdm import tqdm

config = configparser.ConfigParser()
config.read("config.ini")


def wakatime_auth():
    if sys.version_info[0] == 3:
        raw_input = input
    client_id = config["DEFAULT"]["app_id"]
    secret = config["DEFAULT"]["app_secret"]
    service = OAuth2Service(
        client_id=client_id,  # your App ID from https://wakatime.com/apps
        client_secret=secret,  # your App Secret from https://wakatime.com/apps
        name="update-wt",
        authorize_url="https://wakatime.com/oauth/authorize",
        access_token_url="https://wakatime.com/oauth/token",
        base_url="https://wakatime.com/api/v1/",
    )
    redirect_uri = "https://localhost"
    state = hashlib.sha1(os.urandom(40)).hexdigest()
    params = {
        "scope": "email,read_stats,write_logged_time",
        "response_type": "code",
        "state": state,
        "redirect_uri": redirect_uri,
    }
    url = service.get_authorize_url(**params)
    print("**** Visit this url in your browser ****".format(url=url))
    print("*" * 80)
    print(url)
    print("*" * 80)
    print(
        "**** After clicking Authorize, paste code here and press Enter ****"
    )
    code = raw_input("Enter code from url: ")
    # Make sure returned state has not changed for security reasons, and exchange
    # code for an Access Token.
    headers = {"Accept": "application/x-www-form-urlencoded"}
    print("Getting an access token...")
    session = service.get_auth_session(
        headers=headers,
        data={
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        },
    )
    config["DEFAULT"]["access_token"] = session.access_token


def load_json_file(path):
    path = Path(path)
    with open(path, "r") as f:
        j_file = json.load(f)
        return j_file


def timing_to_wakatime_mapper(j_object):
    start_time = parse(j_object["startDate"], fuzzy_with_tokens=True)
    end_time = start_time[0].timestamp() + j_object["duration"]
    wakatime_object = {
        "external_id": j_object["id"],
        "entity": j_object["path"],
        "project": j_object["project"],
        "start_time": start_time[0].timestamp(),
        "end_time": end_time,
    }

    # Add Wakatime Type to object
    if wakatime_object["entity"].startswith("http"):
        wakatime_object["type"] = "domain"
    elif wakatime_object["entity"].startswith("file:"):
        wakatime_object["type"] = "file"

    # Add Wakatime Category to object
    if j_object["application"].startswith("Safari"):
        if "readthedocs.io" in j_object["path"]:
            wakatime_object["category"] = "researching"
        elif "ny-rtem.com" in j_object["path"]:
            wakatime_object["category"] = "researching"
        else:
            wakatime_object["category"] = "browsing"
    elif j_object["application"].startswith("IntelliJ IDEA"):
        wakatime_object["category"] = "coding"
    elif j_object["application"].startswith("Finder"):
        wakatime_object["category"] = "browsing"

    # Add inferred language to object
    try:
        if j_object['activityTitle'].endswith('.py'):
            wakatime_object['language'] = 'Python'
        elif j_object['activityTitle'].endswith('.ipynb'):
            wakatime_object['language'] = 'Jupyter'
        elif j_object['activityTitle'].endswith('.json'):
            wakatime_object['language'] = 'JSON'
    except KeyError:
        wakatime_object['language'] = ''
    return wakatime_object


def post_wakatime_object(w_obj):
    url = config["DEFAULT"]["base_url"] + "users/current/external_durations.bulk"
    headers = {
        "Authorization": f"""Bearer {config['DEFAULT']['access_token']}"""
    }
    data = json.dumps(w_obj)
    r = requests.post(url, data=data, headers=headers)

    return json.loads(r.text)


def main():
    # Timing.app Sample JSON Entry
    # [{
    #     "activityTitle" : "rtem-hackathon [~\/Documents\/Projects\/Hackathons\/rtem-hackathon] – …\/.gitignore",
    #     "application" : "IntelliJ IDEA",
    #     "duration" : 0.99927854537963867,
    #     "endDate" : "2022-04-24T06:37:43Z",
    #     "id" : "3545027914866529280",
    #     "path" : "\/Users\/danlsn\/Documents\/Projects\/Hackathons\/rtem-hackathon",
    #     "project" : "rtem-hackathon",
    #     "startDate" : "2022-04-24T06:37:42Z"
    # }]
    wakatime_response = []
    bulk_data = []
    timing_json = load_json_file("data/rtem-hackathon.json")
    for j_obj in tqdm(timing_json):
        w_obj = timing_to_wakatime_mapper(j_obj)
        bulk_data.append(w_obj)

    res = post_wakatime_object(bulk_data)
    wakatime_response.append(res)

    with open('response.json', 'w') as f:
        f.write(json.dumps(wakatime_response))

    url = config["DEFAULT"]["base_url"] + "users/current/all_time_since_today"
    headers = {
        "Authorization": f"""Bearer {config['DEFAULT']['access_token']}"""
    }
    r = requests.get(url, headers=headers)
    print(r.json())
    # Fields we need for the API Call
    # {
    #   "external_id": <string: unique identifier for this duration on the external
    #                   provider>,
    #   "entity": <string: entity which this duration is logging time towards, such as an absolute file path
    #               or a domain>,
    #   "type": <string: type of entity; can be file, app, or domain>,
    #   "category": <string: category for this activity (optional); normally this is inferred automatically from type;
    #               can be coding, building, indexing, debugging, browsing, running tests, writing tests, manual testing
    #               , writing docs, code reviewing, researching, learning, or designing>,
    #   "start_time": <float: UNIX epoch timestamp when the activity started; numbers after
    #                 decimal point are fractions of a second>,
    #   "end_time": <float: UNIX epoch timestamp when the activity ended;
    #               numbers after decimal point are fractions of a second>,
    #   "project": <string: project name (optional)>,
    #   "branch": <string: branch name (optional)>,
    #   "language": <string: language name (optional)>,
    # }
    return


if __name__ == "__main__":
    main()
