import re
import os
from validators import ip_address, domain, length
from flask import Flask, request, jsonify
from tasks import get_servers, get_vpn_clients, set_servers

app = Flask(__name__)

reg = "(\w\w).+?(protonvpn|nordvpn)\.com"


@app.route('/')
def main():
    """Show Recommended Remote Servers"""
    if "q" in request.args:
        if request.args["q"] in ("protonvpn", "nordvpn"):
            if 'loc' in request.args:
                data = get_servers(provider=request.args["q"], loc=request.args["loc"].upper())
            else:
                data = get_servers(provider=request.args["q"])
            return jsonify(data)
        else:
            return {"Error": "Use ?q=protonvpn For ProtonVPN or ?q=nordvpn For NordVPN"}
    else:
        return {"Error": "Use ?q=protonvpn For ProtonVPN or ?q=nordvpn For NordVPN"}


@app.route('/get_settings')
def pf():
    """Get VPN Client's Remote Server address"""
    if "loc" in request.args:
        location = request.args['loc']
        return jsonify(get_vpn_clients(loc=location))
    else:
        return jsonify(get_vpn_clients())


@app.route('/comp')
def comp():
    """Show Recommended Remote Servers and Current Settings"""
    vpn_clients = get_vpn_clients()
    locations: list = vpn_clients["locations"]

    if "loc" in request.args:
        locations.clear()
        locations.append(request.args["loc"].upper())

    cli: dict = {
        "protonvpn": {},
        "nordvpn": {}
    }

    for loc in locations:
        for provider in ["protonvpn", "nordvpn"]:
            if loc not in cli[provider].keys():
                cli[provider][f"{loc}"] = {"pfsense": []}
            data = get_servers(provider=provider, loc=loc)
            cli[provider][loc].update({ "available_servers": data})

    for client in vpn_clients["clients"]:
        vpn_address = re.match(reg, client)
        if vpn_address:
            vpn_address_groups = vpn_address.groups()
            cli[vpn_address_groups[1]][vpn_address_groups[0]]["pfsense"].append(client)

    return jsonify(cli)


@app.route('/set')
def set():
    """Set Recommended Remote Servers and Current Settings"""
    return jsonify(set_servers())


if __name__ == '__main__':

    if "host-address" in os.environ:
        host = os.getenv("host-address")
        if ip_address.ipv4(host) or ip_address.ipv6(host) or domain(host):
            pass
        else:
            raise Exception("Please verify \"host-address\" was entered correctly")
    else:
        raise Exception("\"host-address\" was not found")

    if "host-port" in os.environ:
        port = os.getenv("host-port")
        if int(port) < 1 or int(port) > 65535:
            pass
        else:
            raise Exception("Please verify \"host-port\" was entered correctly")
    else:
        raise Exception("\"host-port\" was not found")

    if "fauxapi-key" in os.environ:
        key = os.getenv("fauxapi-key")
        if not length(key, min=12, max=40):
            raise Exception("Please verify \"fauxapi-key\" was entered correctly")
    else:
        raise Exception("\"fauxapi-key\" was not found")

    if "fauxapi-secret" in os.environ:
        secret = os.getenv("fauxapi-secret")
        if not length(secret, min=40, max=128):
            raise Exception("Please verify \"fauxapi-secret\" was entered correctly")
    else:
        raise Exception("\"fauxapi-secret\" was not found")

    app.run(host="0.0.0.0", debug=True)
