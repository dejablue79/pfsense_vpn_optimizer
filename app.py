import re
from flask import Flask, request, jsonify
from tasks import get_settings, get_servers

app = Flask(__name__)


@app.route('/')
def main():
    if request.args["q"] in ("pvpn", "nvpn"):
        if 'loc' in request.args:
            data = get_servers(provider=request.args["q"], loc=request.args["loc"].upper())
        else:
            data = get_servers(provider=request.args["q"])
        return jsonify(data)
    else:
        return {"Error": "Use ?q=pvon For ProtonVPN or ?q=nvpn For NordVPN"}


@app.route('/get_settings')
def pf():
    cli = []
    vpn_clients = get_settings()
    for vpnclient in vpn_clients["openvpn-client"]:
        if re.match("(DE0. ProtonVPN)", vpnclient["description"]):
            cli.append(vpnclient["server_addr"])

    return jsonify(cli)


@app.route('/comp')
def comp():
    data = get_servers(provider="pvpn", loc="DE")

    cli = []
    vpn_clients = get_settings()
    for vpnclient in vpn_clients["openvpn-client"]:
        if re.match("(DE0. ProtonVPN)", vpnclient["description"]):
            cli.append(vpnclient["server_addr"])

    return jsonify({"Current": cli, "by_load": data})


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)