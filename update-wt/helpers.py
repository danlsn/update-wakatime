import json
from pathlib import Path
import requests
from main import config


def load_json_file(path):
    path = Path(path)
    with open(path, "r") as f:
        j_file = json.load(f)
        return j_file


def post_wakatime_object(w_obj):
    url = config["DEFAULT"]["base_url"] + "users/current/external_durations.bulk"
    headers = {
        "Authorization": f"""Bearer {config['DEFAULT']['access_token']}"""
    }
    data = json.dumps(w_obj)
    r = requests.post(url, data=data, headers=headers)

    return json.loads(r.text)


def deduce_language(timing_object):
    wakatime_language = None
    try:
        at = timing_object['activityTitle']
    except KeyError:
        return
    try:
        if at.endswith('.py'):
            wakatime_language = 'Python'
        elif at.endswith('.ipynb'):
            wakatime_language = 'Jupyter'
        elif at.endswith('.json'):
            wakatime_language = 'JSON'
    except KeyError:
        return

    if wakatime_language:
        return wakatime_language

    else:
        return

