import re
import os
import requests
from validators import domain
from PfsenseFauxapi.PfsenseFauxapi import PfsenseFauxapi, PfsenseFauxapiException

reg = r"(\w\w).+?(protonvpn|nordvpn)\.com"


def create_api_client() -> PfsenseFauxapi:
    host = os.getenv("HOST_ADDRESS")
    port = os.getenv("HOST_PORT", 443)
    key = os.getenv("FAUXAPI_KEY")
    secret = os.getenv("FAUXAPI_SECRET")

    pfapi = PfsenseFauxapi(f"{host}:{port}", key, secret)
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


def get_vpn_locations(vpn_clients: dict) -> set:
    locations = set()
    for client in vpn_clients["openvpn-client"]:
        loc = re.match(reg, client["server_addr"])
        if loc is not None:
            locations.add(loc[1].lower())
    return locations


def get_vpn_clients() -> dict:
    clients: list = []
    vpn_clients = get_all_settings()
    if "error" in vpn_clients.keys():
        return vpn_clients
    else:
        locations: set = get_vpn_locations(vpn_clients)

        for vpnclient in vpn_clients["openvpn-client"]:
            clients.append(vpnclient["server_addr"])
        return {"clients": clients, "locations": list(locations)}


def get_servers(provider: str, loc: str = None) -> dict:
    data: dict = {}

    if provider == "protonvpn":
        resp = fetch_url("https://api.protonmail.ch/vpn/logicals")
        for server in resp["LogicalServers"]:
            if loc:
                if server["ExitCountry"] == loc.upper() and server["Features"] == 0 and server["Tier"] == 2 \
                        and server["Status"] == 1:
                    if loc.upper() == "US" and server['City'] == 'New York City':
                        data[server["Domain"]] = int(server["Load"])
                    elif loc.upper() != "US":
                        data[server["Domain"]] = int(server["Load"])
            else:
                data = resp["LogicalServers"]

    elif provider == "nordvpn":
        base_url = "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations&limit=10"
        resp: dict = {}
        if loc is not None:
            if loc == "uk":
                loc = "gb"
            countries = fetch_url("https://api.nordvpn.com/v1/servers/countries")
            for country in countries:
                if country["code"] == loc.upper():
                    url = '&filters={"country_id":' + str(country["id"]) + '}'
                    resp = fetch_url(base_url + url)
        else:
            resp = fetch_url(base_url)

        for server in resp:
            data[server["hostname"]] = int(server["load"])
    else:
        return {"Error": "Use ?q=pvon For ProtonVPN or ?q=nvpn For NordVPN"}
    return {k: v for k, v in sorted(data.items(), key=lambda item: item[1])}


def set_servers(renew=None):
    results: dict = {
        "protonvpn": {"old": {},
                      "new": {}
                      },
        "nordvpn": {"old": {},
                    "new": {}
                    }
    }

    pf_vpn_clients = get_all_settings()
    locations = set()
    if renew:
        locations.add(renew)
    else:
        locations = get_vpn_locations(pf_vpn_clients)
    for location in locations:
        protonvpn_servers = get_servers(provider="protonvpn", loc=location)
        nordvpn_servers = get_servers(provider="nordvpn", loc=location)

        new_server: list = []

        for vpn_client in pf_vpn_clients["openvpn-client"]:
            if domain(vpn_client["server_addr"]):  # Make sure VPN client is set as a domain
                if re.findall(r"\d+", vpn_client["server_addr"]):  # Ignore ProtonVPN country servers.
                    check_settings = re.match(reg, vpn_client["server_addr"])
                    if check_settings:
                        pf_client_info = check_settings.groups()
                        if location == pf_client_info[0]:
                            if pf_client_info[1] == "protonvpn" and len(protonvpn_servers) > 0:
                                new_server = next(iter(protonvpn_servers))
                                del protonvpn_servers[new_server]
                            elif pf_client_info[1] == "nordvpn" and len(nordvpn_servers) > 0:
                                new_server = next(iter(nordvpn_servers))
                                del nordvpn_servers[new_server]
                            if new_server != vpn_client["server_addr"]:
                                if location not in results[f"{pf_client_info[1]}"]["new"]:
                                    results[f"{pf_client_info[1]}"]["old"][location] = []
                                    results[f"{pf_client_info[1]}"]["new"][location] = []

                                results[f"{pf_client_info[1]}"]["old"][f"{location}"].append(vpn_client["server_addr"])
                                results[f"{pf_client_info[1]}"]["new"][f"{location}"].append(new_server)
                                vpn_client["server_addr"] = new_server

    checker: int = 0
    for vpn_provider in results:
        if not len(results[vpn_provider]["new"]):
            results[vpn_provider] = "No Need to Update"
            checker += 1

    if checker != 2:
        results["info"] = set_pfsense(data=pf_vpn_clients)
    return results


def replace_vpn_location(provider: str, old: str, new: str) -> dict:
    pf_vpn_clients = get_all_settings()
    for vpn_client in pf_vpn_clients["openvpn-client"]:
        check_settings = re.match(reg, vpn_client["server_addr"])
        if check_settings:
            pf_client_info = check_settings.groups()
            if pf_client_info[1] == provider and pf_client_info[0] == old:
                new_location = vpn_client["server_addr"].replace(old, new, 1)
                vpn_client["server_addr"] = new_location

    set_pfsense(data=pf_vpn_clients)
    return set_servers(renew=new)
