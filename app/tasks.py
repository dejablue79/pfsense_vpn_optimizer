import re
from modules import pfsense
from modules import protonvpn
from modules import nordvpn
from validators import domain

reg = r"(\w\w).+?(protonvpn|nordvpn)\.com"
providers = ["protonvpn", "nordvpn"]

pf_api = pfsense.PfSense()
protonvpn_api = protonvpn.ProtonVPN()
nordvpn_api = nordvpn.NordVPN()


def get_vpn_servers(provider: str, loc: str) -> dict:
    if provider == "protonvpn":
        data = protonvpn_api.receive_servers_list(loc=loc)
        return data
    if provider == "nordvpn":
        data = nordvpn_api.receive_servers_list(loc=loc)
        return data


def compare_servers():
    vpn_clients = pf_api.get_pf_openvpn_clients()
    locations: list = vpn_clients["locations"]

    results: dict = {}

    for provider in providers:
        results[provider] = {}
        for loc in locations:
            results[provider][loc] = {"pfsense": {}}
            data = get_vpn_servers(provider=provider, loc=loc)
            results[provider][loc].update({"available_servers": data})

    for client in vpn_clients["clients"]:
        vpn_address = re.match(reg, client)
        if vpn_address:
            vpn_address_groups = vpn_address.groups()
            alpha_code = vpn_address_groups[0]
            provider = vpn_address_groups[1]
            if client in results[provider][alpha_code]["available_servers"].keys():
                results[provider][alpha_code]["pfsense"][client] = \
                    results[provider][alpha_code]["available_servers"][client]
            else:
                results[provider][alpha_code]["pfsense"][client] = None
    results_clean = list()
    for provider in results.keys():
        for location in results[provider]:
            if not len(results[provider][location]["pfsense"]):
                results_clean.append([provider, location])
    for location in results_clean:
        results[location[0]].pop(location[1])

    return results


def set_servers(renew=None):
    results: dict = {
        "protonvpn": {},
        "nordvpn": {}
    }

    pf_vpn_clients = pf_api.get_openvpn_settings()

    available_servers: dict = {}
    new_server: list = []
    locations = set()
    vpn_id = list()

    if renew:
        locations.add(renew)
    else:
        locations = pf_api.get_pf_openvpn_locations(pf_vpn_clients)

    for location in locations:
        for provider in providers:
            if provider not in available_servers.keys():
                available_servers[provider] = {}
            available_servers[provider].update({location: {}})
            data = get_vpn_servers(provider=provider, loc=location)
            available_servers[provider][location] = data

    for vpn_client in pf_vpn_clients["openvpn-client"]:
        if domain(vpn_client["server_addr"]):  # Make sure VPN client is set as a domain
            if re.findall(r"\d+", vpn_client["server_addr"]):  # Ignore ProtonVPN country servers.
                check_settings = re.match(reg, vpn_client["server_addr"])
                if check_settings:
                    pf_client_info = check_settings.groups()
                    location = pf_client_info[0]
                    provider = pf_client_info[1]

                    new_server = next(iter(available_servers[provider][location]))
                    del available_servers[provider][location][new_server]

                    if new_server != vpn_client["server_addr"]:
                        if location not in results[provider]:
                            results[provider][location] = {}
                            results[provider][location]["old"] = []
                            results[provider][location]["new"] = []

                        results[provider][location]["old"].append(vpn_client["server_addr"])
                        results[provider][location]["new"].append(new_server)
                        vpn_client["server_addr"] = new_server
                        vpn_id.append(vpn_client["vpnid"])
    checker: int = 0
    for vpn_provider in results:
        for location in results[vpn_provider].keys():
            if not len(results[vpn_provider][location]["new"]) or not len(results[vpn_provider].keys()):
                results[vpn_provider] = "No Need to Update"
                checker += 1
    if checker != len(providers):
        results["info"] = pf_api.set_pfsense_config(data=pf_vpn_clients, vpnid=vpn_id, refresh=True)
    return results


def replace_vpn_location(provider: str, old: str, new: str) -> dict:
    vpn_id = list()
    pf_vpn_clients = pf_api.get_openvpn_settings()
    for vpn_client in pf_vpn_clients["openvpn-client"]:
        check_settings = re.match(reg, vpn_client["server_addr"])
        if check_settings:
            pf_client_info = check_settings.groups()
            if pf_client_info[1] == provider and pf_client_info[0] == old:
                new_location = vpn_client["server_addr"].replace(old, new, 1)
                vpn_client["server_addr"] = new_location
                vpn_id.append(vpn_client["vpn_id"])
    pf_api.set_pfsense_config(data=pf_vpn_clients, vpnid=vpn_id)
    return set_servers(renew=new)
