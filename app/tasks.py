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

    results: dict = {
        "protonvpn": {},
        "nordvpn": {}
    }

    for loc in locations:
        for provider in ["protonvpn", "nordvpn"]:
            if loc not in results[provider].keys():
                results[provider][f"{loc}"] = {"pfsense": {}}
            if provider == "protonvpn":
                data = get_vpn_servers(provider="protonvpn", loc=loc)
                results[provider][loc].update({"available_servers": data})
            if provider == "nordvpn":
                data = get_vpn_servers(provider="nordvpn", loc=loc)
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
    locations = set()
    vpnid = list()

    if renew:
        locations.add(renew)
    else:
        locations = pf_api.get_pf_openvpn_locations(pf_vpn_clients)
    for location in locations:
        protonvpn_servers = get_vpn_servers(provider="protonvpn", loc=location)
        nordvpn_servers = get_vpn_servers(provider="nordvpn", loc=location)

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
                                if location not in results[f"{pf_client_info[1]}"]:
                                    results[f"{pf_client_info[1]}"][location] = {}
                                    results[f"{pf_client_info[1]}"][location]["old"] = []
                                    results[f"{pf_client_info[1]}"][location]["new"] = []

                                results[f"{pf_client_info[1]}"][f"{location}"]["old"].append(vpn_client["server_addr"])
                                results[f"{pf_client_info[1]}"][f"{location}"]["new"].append(new_server)
                                vpn_client["server_addr"] = new_server
                                vpnid.append(vpn_client["vpnid"])

    checker: int = 0
    for vpn_provider in results:
        for location in results[vpn_provider].keys():
            if not len(results[vpn_provider][location]["new"]) or not len(results[vpn_provider].keys()):
                results[vpn_provider] = "No Need to Update"
                checker += 1
    if checker != 2:
        results["info"] = pf_api.set_pfsense_config(data=pf_vpn_clients, vpnid=vpnid, refresh=True)
    return results


def replace_vpn_location(provider: str, old: str, new: str) -> dict:
    vpnid = list()
    pf_vpn_clients = pf_api.get_openvpn_settings()
    for vpn_client in pf_vpn_clients["openvpn-client"]:
        check_settings = re.match(reg, vpn_client["server_addr"])
        if check_settings:
            pf_client_info = check_settings.groups()
            if pf_client_info[1] == provider and pf_client_info[0] == old:
                new_location = vpn_client["server_addr"].replace(old, new, 1)
                vpn_client["server_addr"] = new_location
                vpnid.append(vpn_client["vpnid"])
    pf_api.set_pfsense_confi(data=pf_vpn_clients, vpnid=[])
    return set_servers(renew=new)
