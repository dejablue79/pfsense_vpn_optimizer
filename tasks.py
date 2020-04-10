import re
import os
import requests


def get_all_settings() -> dict:
    from PfsenseFauxapi.PfsenseFauxapi import PfsenseFauxapi
    host = os.getenv("host-address")
    key = os.getenv("fauxapi-key")
    secret = os.getenv("fauxapi-secre")
    PfsenseFauxapi = PfsenseFauxapi(host, key, secret)
    openvpn_settings = PfsenseFauxapi.config_get('openvpn')
    return openvpn_settings


def get_vpn_clients(loc: str = None) -> list:
    clients = []
    locations: list = ["DE", "US"]
    vpn_clients = get_all_settings()
    if loc:
        locations.clear()
        locations.append(loc.upper())
    for loc in locations:
        for vpnclient in vpn_clients["openvpn-client"]:
            if re.match(f"{loc}0. ProtonVPN", vpnclient["description"]):
                clients.append(vpnclient["server_addr"])
            if re.match(f"{loc} NordVPN", vpnclient["description"]):
                clients.append(vpnclient["server_addr"])
    return clients


def get_servers(provider: str, loc: str = None) -> dict:
    data: dict = {}

    if provider == "pvpn":
        r = requests.get("https://api.protonmail.ch/vpn/logicals")
        resp = r.json()
        for server in resp["LogicalServers"]:
            if server["ExitCountry"] == loc and server["Features"] == 0 and server["Tier"] >= 1:
                if loc == "US" and server['City'] == 'New York City':
                    data[int(server["Load"])] = server["Domain"]
                elif loc != "US":
                    data[int(server["Load"])] = server["Domain"]
                    if len(data.keys()) > 5:
                        break
    elif provider == "nvpn":
        if loc is not None:
            r = requests.get("https://api.nordvpn.com/server")
        else:
            r = requests.get("https://api.nordvpn.com/v1/servers/recommendations")
        resp = r.json()
        for server in resp:
            if "flag" in server:
                if server["flag"] == loc:
                    data[int(server["load"])] = server["domain"]
                    if len(data.keys()) > 5:
                        break
            else:
                if server["status"] == "online":
                    data[int(server["load"])] = server["hostname"]
    else:
        return {"Error": "Use ?q=pvon For ProtonVPN or ?q=nvpn For NordVPN"}
    return data
