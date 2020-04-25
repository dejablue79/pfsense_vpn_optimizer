import re
import os
import requests
from PfsenseFauxapi.PfsenseFauxapi import PfsenseFauxapi, PfsenseFauxapiException


reg = "(\w\w).+?(protonvpn|nordvpn)\.com"


def create_api_client() -> PfsenseFauxapi:
    host = os.getenv("host-address")
    key = os.getenv("fauxapi-key")
    secret = os.getenv("fauxapi-secret")

    pfapi = PfsenseFauxapi(host, key, secret)
    return pfapi


def fetch_url(url: str) -> dict:
    try:
        r = requests.get(url)
    except requests.HTTPError as e:
        print(e)
    else:
        return r.json()


def get_all_settings() -> dict:
    try:
        pfapi = create_api_client()
        openvpn_settings = pfapi.config_get('openvpn')
    except PfsenseFauxapiException as e:
        return {"error": str(e)}
    else:
        return openvpn_settings


def set_pfsense(data: dict) -> dict:
    try:
        pfapi = create_api_client()
        resp = pfapi.config_set(data, 'openvpn')
    except PfsenseFauxapiException as e:
        return {"error": str(e)}
    else:
        pfapi.config_reload()
        return resp


def get_vpn_locals(vpn_clients: dict) -> list:
    locations = set()
    for client in vpn_clients["openvpn-client"]:
        loc = re.match(reg, client["server_addr"])
        if loc is not None:
            locations.add(loc[1].lower())
    return locations


def get_vpn_clients(loc: str = None) -> dict:
    clients: list = []
    vpn_clients = get_all_settings()
    if "error" in vpn_clients.keys():
        return vpn_clients
    else:
        locations: set = get_vpn_locals(vpn_clients)
        if loc:
            locations.clear()
            locations.add(loc.lower())
        for loc in locations:
            for vpnclient in vpn_clients["openvpn-client"]:
                locals = re.search(reg, vpnclient["server_addr"])
                if locals:
                    if loc in locals.groups():
                        clients.append(vpnclient["server_addr"])
        return {"clients": clients, "locations": list(locations)}


def get_servers(provider: str, loc: str = None) -> dict:
    data: dict = {}

    if provider == "pvpn":
        resp = fetch_url("https://api.protonmail.ch/vpn/logicals")
        for server in resp["LogicalServers"]:
            if server["ExitCountry"] == loc.upper() and server["Features"] == 0 and server["Tier"] == 2 and server["Status"] == 1:
                if loc.upper() == "US" and server['City'] == 'New York City':
                    data[int(server["Load"])] = server["Domain"]
                elif loc.upper() != "US":
                    data[int(server["Load"])] = server["Domain"]
    elif provider == "nvpn":
        base_url = "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations"
        resp: dict
        if loc is not None:
            countries = fetch_url("https://api.nordvpn.com/v1/servers/countries")
            for country in countries:
                if country["code"] == loc.upper():
                    url = '&filters={"country_id":' + str(country["id"]) + '}'
                    resp = fetch_url(base_url + url)
        else:
            resp = fetch_url(base_url)

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
    locations: list = get_vpn_locals(vpn_clients)
    for loc in locations:
        pdata = get_servers(provider="pvpn", loc=loc)
        ndata = get_servers(provider="nvpn", loc=loc)

        sorted_pdata: dict = sorted(pdata.items())
        sorted_ndata: dict = sorted(ndata.items())

        print(len(ndata.items()))

        for vpnclient in vpn_clients["openvpn-client"]:
            settings = re.match(reg, vpnclient["server_addr"])
            if settings:
                data = settings.groups()
                if loc == data[0] and data[1] == "protonvpn"and len(sorted_pdata) > 0:
                    server = next(iter(sorted_pdata))
                    del sorted_pdata[0]
                    if server[1] != vpnclient["server_addr"]:
                        res["protonVPN"]["old"].append(vpnclient["server_addr"])
                        res["protonVPN"]["new"].append(server[1])
                        vpnclient["server_addr"] = server[1]
                elif loc == data[0] and data[1] == "nordvpn" and len(sorted_ndata) > 0:
                    server = next(iter(sorted_ndata))
                    del sorted_ndata[0]
                    if server[1] != vpnclient["server_addr"]:
                        res["NordVPN"]["old"].append(vpnclient["server_addr"])
                        res["NordVPN"]["new"].append(server[1])
                        vpnclient["server_addr"] = server[1]
                elif not len(ndata.items()):
                    res["NordVPN"]["old"].append(vpnclient["server_addr"])
                    res["NordVPN"]["new"].append(f"Unable to fetch new servers for {loc}.")

    res["info"] = set_pfsense(data=vpn_clients)
    return res
