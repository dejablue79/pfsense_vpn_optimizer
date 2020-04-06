import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def hello_world():
    data: dict = {}
    if 'loc' in request.args:
        loc = request.args["loc"].upper()
    if request.args["q"] == "pvpn":
        r = requests.get("https://api.protonmail.ch/vpn/logicals")
        resp = r.json()
        for server in resp["LogicalServers"]:
            if server["ExitCountry"] == loc and server["Features"] == 0 and server["Tier"] >= 1:
                if loc == "us" and server['City'] == 'New York City':
                    data[int(server["Load"])] = server["Domain"]
    elif request.args["q"] == "nvpn":
        if 'loc' not in request.args:
            r = requests.get("https://api.nordvpn.com/v1/servers/recommendations")
        else:
            r = requests.get("https://api.nordvpn.com/server")
        resp = r.json()
        for server in resp:
            if "flag" in server:
                if server["flag"] == loc:
                    data[int(server["load"])] = server["domain"]
            else:
                data[int(server["load"])] = server["hostname"]
    return jsonify(data)


@app.route('/pf')
def pf():
    from PfsenseFauxapi.PfsenseFauxapi import PfsenseFauxapi
    host = os.getenv("host-address")
    key = os.getenv("fauxapi-key")
    secret = os.getenv("fauxapi-secre")
    PfsenseFauxapi = PfsenseFauxapi(host, key, secret)
    openvpn_settings = PfsenseFauxapi.config_get('openvpn')
    ## perform some kind of manipulation to `aliases` here ##
    # pprint.pprint(PfsenseFauxapi.config_set(aliases, 'aliases'))
    return openvpn_settings


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)