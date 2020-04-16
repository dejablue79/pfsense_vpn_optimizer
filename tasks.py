import re
import os
import requests

from PfsenseFauxapi.PfsenseFauxapi import PfsenseFauxapi
host = os.getenv("host-address")
key = os.getenv("fauxapi-key")
secret = os.getenv("fauxapi-secre")
PfsenseFauxapi = PfsenseFauxapi(host, key, secret)


def get_all_settings() -> dict:
    openvpn_settings = PfsenseFauxapi.config_get('openvpn')
    return openvpn_settings


def set_pfsense(data:dict) -> dict:
    resp = PfsenseFauxapi.config_set(data, 'openvpn')
    PfsenseFauxapi.config_reload()
    return resp


def get_vpn_locals() -> list:
    reg = "(\w\w).+?(protonvpn|nordvpn)\.com"
    locations = set()
    vpn_clients = get_all_settings()
    for client in vpn_clients["openvpn-client"]:
        loc = re.match(reg, client["server_addr"])
        if loc is not None:
            locations.add(loc[1].upper())
    return locations


def get_vpn_clients(loc: str = None) -> list:
    clients: list = []
    locations: list = get_vpn_locals()
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
    elif provider == "nvpn":
        base_url = "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations"
        if loc is not None:
            countries = requests.get("https://api.nordvpn.com/v1/servers/countries")
            for country in countries.json():
                if country["code"] == loc:
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

        sorted_pdata = dict(sorted(pdata.items()))
        sorted_ndata = dict(sorted(ndata.items()))

        for vpnclient in vpn_clients["openvpn-client"]:
            if re.match(f"{loc}0. ProtonVPN", vpnclient["description"]):
                server = next(iter(sorted_pdata))
                del sorted_pdata[server]
                if pdata[server] != vpnclient["server_addr"]:
                    res["protonVPN"]["old"].append(vpnclient["server_addr"])
                    res["protonVPN"]["new"].append(pdata[server])
                    vpnclient["server_addr"] = pdata[server]
            if re.match(f"{loc} NordVPN", vpnclient["description"]):
                server = next(iter(sorted_ndata))
                del sorted_ndata[server]
                if ndata[int(server)] != vpnclient["server_addr"]:
                    res["NordVPN"]["old"].append(vpnclient["server_addr"])
                    res["NordVPN"]["new"].append(ndata[server])
                    vpnclient["server_addr"] = ndata[server]
                    # del ndata[server]
    res["info"] = set_pfsense(data=vpn_clients)
    return res
