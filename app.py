import re
from flask import Flask, request, jsonify
from tasks import get_all_settings, get_servers, get_vpn_clients

app = Flask(__name__)


@app.route('/')
def main():
    if "q" in request.args:
        if request.args["q"] in ("pvpn", "nvpn"):
            if 'loc' in request.args:
                data = get_servers(provider=request.args["q"], loc=request.args["loc"].upper())
            else:
                data = get_servers(provider=request.args["q"])
            return jsonify(data)
        else:
            return {"Error": "Use ?q=pvon For ProtonVPN or ?q=nvpn For NordVPN"}
    else:
        return {"Error": "Use ?q=pvon For ProtonVPN or ?q=nvpn For NordVPN"}


@app.route('/get_settings')
def pf():
    """Get VPN Client's Remote Server address"""
    return jsonify(get_vpn_clients())


@app.route('/comp')
def comp():
    """Show Recommended Remote Servers and Current Settings"""
    locations: list = ["DE", "US"]
    vpn_clients = get_vpn_clients()

    if "loc" in request.args:
        locations.clear()
        locations.append(request.args["loc"].upper())

    cli: dict = {
        "protonVPN": {},
        "NordVPN": {}
    }

    for loc in locations:
        pdata = get_servers(provider="pvpn", loc=loc)
        ndata = get_servers(provider="nvpn", loc=loc)
        cli["protonVPN"][loc] = {
            "pfsense": [],
            "available_servers": pdata
            }
        cli["NordVPN"][loc] = {
            "pfsense": [],
            "available_servers": ndata
        }

        for client in vpn_clients:
            if re.match(f"{loc}\-.*\.protonvpn\.com", client, re.IGNORECASE):
                cli["protonVPN"][loc]["pfsense"].append(client)
            if re.match(f"{loc}.+\.nordvpn\.com", client, re.IGNORECASE):
                cli["NordVPN"][loc]["pfsense"].append(client)
    return jsonify(cli)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)