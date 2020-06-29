import re
import os
from validators import ip_address, domain, length
from flask import Flask, request, jsonify

from tasks import pf_api, protonvpn_api, nordvpn_api, get_vpn_servers, set_servers, compare_servers, replace_vpn_location

app = Flask(__name__)

reg = r"(\w\w).+?(protonvpn|nordvpn)\.com"


@app.route('/')
def main():
    """Show Recommended Remote Servers"""
    if "q" in request.args:
        if request.args["q"] in ("protonvpn", "nordvpn"):
            if 'loc' in request.args:
                if len(request.args["loc"]) == 2:
                    data = get_vpn_servers(provider=request.args["q"], loc=request.args["loc"].upper())
                else:
                    return {"Error": "loc should be two letters country code"}
            else:
                data = get_vpn_servers(provider=request.args["q"])
            return jsonify(data)
        else:
            return {"Error": "Use ?q=protonvpn For ProtonVPN or ?q=nordvpn For NordVPN"}
    else:
        return {"Error": "Use ?q=protonvpn For ProtonVPN or ?q=nordvpn For NordVPN"}


@app.route('/get_settings')
def pf():
    """Get VPN Client's Remote Server address"""
    return jsonify(pf_api.get_pf_openvpn_clients())


@app.route('/compare')
def comp():
    """Show Recommended Remote Servers and Current Settings"""
    return jsonify(compare_servers())


@app.route('/set')
def set_pf_clients():
    """Set Recommended Remote Servers and Current Settings"""
    return jsonify(set_servers())


@app.route('/replace/<path:provider>')
def replace(provider):
    if provider in ["protonvpn", "nordvpn"]:
        if "loc" in request.args:
            if not len(request.args["loc"]) == 2:
                return {"Error": "loc should be two letters country code"}
        if "with" in request.args:
            if not len(request.args["with"]) == 2:
                return {"Error": "with should be two letters country code"}
        data = replace_vpn_location(provider=provider, old=request.args["loc"], new=request.args["with"])
        return jsonify(data)
    else:
        return {"Error": "Provider can be protonvpn or nordvpn"}


if __name__ == '__main__':

    if "HOST_ADDRESS" in os.environ:
        host = os.getenv("HOST_ADDRESS")
        if ip_address.ipv4(host) or ip_address.ipv6(host) or domain(host):
            pass
        else:
            raise Exception("Please verify \"HOST_ADDRESS\" was entered correctly")
    else:
        raise Exception("\"HOST_ADDRESS\" was not found")

    # if "HOST_PORT" in os.environ:
    #     port = os.getenv("HOST_PORT", 443)
    #     if 1 <= int(port) <= 65535:
    #         pass
    #     else:
    #         raise Exception("Please verify \"HOST_PORT\" was entered correctly")

    if "FAUXAPI_KEY" in os.environ:
        key = os.getenv("FAUXAPI_KEY")
        if not length(key, min=12, max=40) or not key.startswith("PFFA"):
            raise Exception("Please verify \"FAUXAPI_KEY\" was entered correctly")
    else:
        raise Exception("\"FAUXAPI_KEY\" was not found")

    if "FAUXAPI_SECRET" in os.environ:
        secret = os.getenv("FAUXAPI_SECRET")
        if not length(secret, min=40, max=128):
            raise Exception("Please verify \"FAUXAPI_SECRET\" was entered correctly")
    else:
        raise Exception("\"FAUXAPI_SECRET\" was not found")

    app.run(host="0.0.0.0", debug=True)
