import re
import os
import requests
from PfsenseFauxapi.PfsenseFauxapi import PfsenseFauxapi

host = os.getenv("host-address")
key = os.getenv("fauxapi-key")
secret = os.getenv("fauxapi-secret")

PfsenseFauxapi = PfsenseFauxapi(host, key, secret)

reg = "(\w\w).+?(protonvpn|nordvpn)\.com"


def get_all_settings() -> dict:
    openvpn_settings = PfsenseFauxapi.config_get('openvpn')
    return openvpn_settings


def set_pfsense(data:dict) -> dict:
    resp = PfsenseFauxapi.config_set(data, 'openvpn')
    PfsenseFauxapi.config_reload()
    return resp


def get_vpn_locals() -> list:
    locations = set()
    vpn_clients = get_all_settings()
    for client in vpn_clients["openvpn-client"]:
        loc = re.match(reg, client["server_addr"])
        if loc is not None:
            locations.add(loc[1].lower())
    return locations


def get_vpn_clients(loc: str = None) -> list:
    clients: list = []
    locations: set = get_vpn_locals()
    vpn_clients = get_all_settings()
    if loc:
        locations.clear()
        locations.add(loc.lower())
    for loc in locations:
        for vpnclient in vpn_clients["openvpn-client"]:
            locals = re.search(reg, vpnclient["server_addr"])
            if locals:
                if loc in locals.groups():
                    clients.append(vpnclient["server_addr"])
    return clients


def get_servers(provider: str, loc: str = None) -> dict:
    data: dict = {}

    if provider == "pvpn":
        r = requests.get("https://api.protonmail.ch/vpn/logicals")
        resp = r.json()
        for server in resp["LogicalServers"]:
            if server["ExitCountry"] == loc.upper() and server["Features"] == 0 and server["Tier"] > 1 and server["Status"] == 1:
                if loc.upper() == "US" and server['City'] == 'New York City':
                    data[int(server["Load"])] = server["Domain"]
                elif loc.upper() != "US":
                    data[int(server["Load"])] = server["Domain"]
    elif provider == "nvpn":
        base_url = "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations"
        if loc is not None:
            countries = requests.get("https://api.nordvpn.com/v1/servers/countries")
            for country in countries.json():
                if country["code"] == loc.upper():
                    url = '&filters={"country_id":' + str(country["id"]) + '}'
                    r = requests.get(base_url + url)
        else:
            r = requests.get(base_url)
        resp = r.json()
        for server in resp:
            data[int(server["load"])] = server["hostname"]
    else:
        return {"Error": "Use ?q=pvon For ProtonVPN or ?q=nvpn For NordVPN"}
    return data


def set_servers():
    res: dict = {
        "protonVPN": {"old": [],
                      "new": []
                      },
        "NordVPN": {"old": [],
                    "new": []
                    }
    }
    vpn_clients = get_all_settings()
    locations: list = get_vpn_locals()
    for loc in locations:
        pdata = get_servers(provider="pvpn", loc=loc)
        ndata = get_servers(provider="nvpn", loc=loc)

        sorted_pdata: dict = sorted(pdata.items())
        sorted_ndata: dict = sorted(ndata.items())

        for vpnclient in vpn_clients["openvpn-client"]:
            settings = re.match(reg, vpnclient["server_addr"])
            if settings:
                data = settings.groups()
                if loc == data[0] and data[1] == "protonvpn":
                    server = next(iter(sorted_pdata))
                    del sorted_pdata[0]
                    if server[1] != vpnclient["server_addr"]:
                        res["protonVPN"]["old"].append(vpnclient["server_addr"])
                        res["protonVPN"]["new"].append(server[1])
                        vpnclient["server_addr"] = server[1]
                elif loc == data[0] and data[1] == "nordvpn":
                    server = next(iter(sorted_ndata))
                    del sorted_ndata[0]
                    if server[1] != vpnclient["server_addr"]:
                        res["NordVPN"]["old"].append(vpnclient["server_addr"])
                        res["NordVPN"]["new"].append(server[1])
                        vpnclient["server_addr"] = server[1]

    res["info"] = set_pfsense(data=vpn_clients)
    return res
