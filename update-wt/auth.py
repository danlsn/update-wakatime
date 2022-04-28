import hashlib
import os
import sys

from rauth import OAuth2Service

from config import config

from wsgiref.simple_server import make_server
from cgi import parse

from bottle import run, route, request, response, template

from main import config


@route("/")
def capture_params():
    code = request.query.code
    state = request.query.state
    return template("Code: {{id}}, State: {{page}})", id=code, page=state)


# def demo_app(environ, start_response):
#     from io import StringIO
#
#     stdout = StringIO()
#     print("Secret Code: ", file=stdout)
#     print(file=stdout)
#     query_string = environ["QUERY_STRING"].split("&")
#     code = query_string[0][5:-1]
#     print(parse(environ["QUERY_STRING"]), file=stdout)
#     start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
#     return [code]
#
#
# def show_get_params(environ, start_response):
#     status = "200 OK"  # HTTP Status
#     headers = [("Content-type", "text/plain; charset=utf-8")]  # HTTP Headers
#     start_response(status, headers)
#
#     return environ["QUERY_STRING"]


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
    redirect_uri = "http://localhost:3000"
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

    r un(host="localhost", port=3000, debug=True)
    print(
        "**** After clicking Authorize, paste code here and press Enter ****"
    )


    # with make_server("", 3000, demo_app) as httpd:
    #     print("Serving HTTP on port 3000...")
    #
    #     # Alternative: serve one request, then exit
    #     httpd.handle_request()
    #     code = secret

    code = raw_input()

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
    print(session.access_token)
    config["DEFAULT"]["access_token"] = session.access_token


if __name__ == "__main__":
    wakatime_auth()


def wakatime_auth_old():
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