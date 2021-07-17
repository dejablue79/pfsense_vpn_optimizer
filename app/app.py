import os
from validators import ip_address, domain, length
from flask import Flask, request, jsonify
from tasks import pf_api, protonvpn_api, nordvpn_api, \
    get_vpn_servers, set_servers, compare_servers, \
    replace_vpn_location
from modules.helpers import is_supported_provider

app = Flask(__name__)


@app.before_first_request
def check_env():
    if "HOST_ADDRESS" not in os.environ:
        raise Exception("\"HOST_ADDRESS\" was not found")

    if "FAUXAPI_KEY" not in os.environ:
        raise Exception("\"FAUXAPI_KEY\" was not found")

    if "FAUXAPI_SECRET" not in os.environ:
        raise Exception("\"FAUXAPI_SECRET\" was not found")

    host = os.getenv("HOST_ADDRESS")
    valid_host: bool = False

    if ip_address.ipv4(host):
        valid_host = True

    if ip_address.ipv6(host):
        valid_host = True

    if domain(host):
        valid_host = True

    if not valid_host:
        raise Exception("Please verify \"HOST_ADDRESS\" was entered correctly")

    key = os.getenv("FAUXAPI_KEY")
    if not length(key, min=12, max=40) or not key.startswith("PFFA"):
        raise Exception("Please verify \"FAUXAPI_KEY\" was entered correctly")

    secret = os.getenv("FAUXAPI_SECRET")
    if not length(secret, min=40, max=128):
        raise Exception("Please verify \"FAUXAPI_SECRET\" was entered correctly")


@app.route('/')
def main():
    """Show Recommended Remote Servers"""
    if "q" not in request.args:
        return {"Error": "Use ?q=protonvpn For ProtonVPN or ?q=nordvpn For NordVPN"}
    elif not is_supported_provider(request.args["q"]):
        return {"Error": "Use ?q=protonvpn For ProtonVPN or ?q=nordvpn For NordVPN"}
    elif 'loc' in request.args and len(request.args["loc"]) != 2:
        return {"Error": "loc should be two letters country code"}
    elif 'loc' not in request.args:
        data = get_vpn_servers(provider=request.args["q"])
    else:
        data = get_vpn_servers(provider=request.args["q"], loc=request.args["loc"].upper())

    return jsonify(data)


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
    if not is_supported_provider(provider):
        return {"Error": "Provider can be protonvpn or nordvpn"}

    if "loc" in request.args and len(request.args["loc"]) != 2:
        return {"Error": "loc should be two letters country code"}

    if "with" in request.args and len(request.args["with"]) != 2:
        return {"Error": "with should be two letters country code"}

    data = replace_vpn_location(
        provider=provider,
        old=request.args["loc"],
        new=request.args["with"])

    return jsonify(data)


if __name__ == '__main__':
    debug = os.getenv("DEBUG", False)
    app.run(host="0.0.0.0", debug=debug)
