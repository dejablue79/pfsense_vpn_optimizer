import re

from modules import pfsense
from modules import protonvpn
from modules import nordvpn
from validators import domain
from modules.helpers import is_vpn_address, \
    is_supported_provider, \
    get_providers

pf_api = pfsense.PfSense()
protonvpn_api = protonvpn.ProtonVPN()
nordvpn_api = nordvpn.NordVPN()


def get_vpn_servers(provider: str, loc: str) -> dict:
    if provider == "protonvpn":
        data = protonvpn_api.receive_servers_list(loc=loc)
        return data
    elif provider == "nordvpn":
        data = nordvpn_api.receive_servers_list(loc=loc)
        return data
    else:
        raise Exception(f"Provider {provider} is not supported.")


def compare_servers():
    vpn_clients = pf_api.get_pf_openvpn_clients()
    locations: list = vpn_clients["locations"]
    results: dict = {}

    for provider in get_providers():
        results[provider] = dict()
        for location in locations:
            results[provider][location] = {"pfsense": {}}
            data = get_vpn_servers(provider=provider, loc=location)
            results[provider][location].update({"available_servers": data})

    for client in vpn_clients["clients"]:
        vpn_address = is_vpn_address(client)

        if not vpn_address:
            continue

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


def set_servers(renew=None, renew_provider=None):
    results: dict = {
        "protonvpn": dict(),
        "nordvpn": dict()
    }

    pf_vpn_clients = pf_api.get_openvpn_settings()

    available_servers: dict = dict()
    vpn_id: list = list()

    for vpn_client in pf_vpn_clients["openvpn-client"]:
        if not domain(vpn_client["server_addr"]):  # Make sure VPN client is set as a domain
            continue

        if not re.findall(r"\d+", vpn_client["server_addr"]):  # Ignore ProtonVPN country servers.
            continue

        vpn_address = is_vpn_address(vpn_client["server_addr"])
        if not vpn_address:
            continue

        pf_client_info = vpn_address.groups()
        location = pf_client_info[0]
        provider = pf_client_info[1]

        if renew and renew_provider:
            if renew != location or renew_provider != provider:
                continue

        if provider not in available_servers.keys():
            available_servers[provider] = {}

        if location not in available_servers[provider]:
            available_servers[provider].update({location: {}})
            data = get_vpn_servers(provider=provider, loc=location)
            available_servers[provider][location] = data

        new_server: dict = next(iter(available_servers[provider][location]))
        del available_servers[provider][location][new_server]

        if new_server != vpn_client["server_addr"]:
            if location not in results[provider]:
                results[provider][location] = {}
                results[provider][location]["old"] = []
                results[provider][location]["new"] = []

            if not renew and not renew_provider:
                results[provider][location]["old"].append(
                    vpn_client["server_addr"])
            results[provider][location]["new"].append(new_server)
            vpn_client["server_addr"] = new_server
            vpn_id.append(vpn_client["vpnid"])

    checker: int = 0
    for vpn_provider in results:
        if not len(results[vpn_provider].keys()):
            results[vpn_provider] = "No Need to Update"
            checker += 1

    if checker != len(get_providers()):
        results["info"] = pf_api.set_pfsense_config(
            data=pf_vpn_clients,
            vpnid=vpn_id, refresh=True)

    return results


def replace_vpn_location(provider: str, old: str, new: str) -> dict:
    pf_vpn_clients = pf_api.get_openvpn_settings()
    for vpn_client in pf_vpn_clients["openvpn-client"]:
        vpn_address = is_vpn_address(vpn_client["server_addr"])
        if not vpn_address:
            continue

        pf_client_info = vpn_address.groups()
        if pf_client_info[1] == provider and pf_client_info[0] == old:
            new_location = vpn_client["server_addr"].replace(old, new, 1)
            vpn_client["server_addr"] = new_location

    pf_api.set_pfsense_config(data=pf_vpn_clients, vpnid=[])
    return set_servers(renew=new, renew_provider=provider)
