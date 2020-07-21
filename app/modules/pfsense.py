from PfsenseFauxapi.PfsenseFauxapi import PfsenseFauxapi, PfsenseFauxapiException
from os import getenv
from modules.helpers import is_vpn_address


class PfSense:
    """
    PfSense Thingy...
    ...
    Methods
    -------
    get_openvpn_settings(self) -> dict:
    set_pfsense_config(self, data: dict, vpnid: list, refresh: bool = None) -> dict:
    get_pf_openvpn_clients(self) -> dict:
    get_pf_openvpn_locations(self, vpn_clients: dict) -> set:
    """
    def __init__(self):
        self.host = getenv("HOST_ADDRESS")
        self.port = 443
        self.key = getenv("FAUXAPI_KEY")
        self.secret = getenv("FAUXAPI_SECRET")
        self.pfapi = PfsenseFauxapi(f"{self.host}:{self.port}", self.key, self.secret)

    def get_openvpn_settings(self) -> dict:
        try:
            pf_openvpn_settings = self.pfapi.config_get('openvpn')
        except PfsenseFauxapiException as e:
            return {"error": str(e)}
        else:
            return pf_openvpn_settings

    def set_pfsense_config(self, data: dict, vpnid: list, refresh: bool = None) -> dict:
        """
        Parameters
        ----------
        data : dict
            .
        vpnid : list
            .
        refresh : bool
            .
        """
        try:
            resp = self.pfapi.config_set(data, 'openvpn')
        except PfsenseFauxapiException as e:
            return {"error": str(e)}
        else:
            if refresh:
                self.pfapi.config_reload()
            if len(vpnid):
                for vid in vpnid:
                    data = self.pfapi.function_call({"function": "openvpn_restart_by_vpnid", "args": ["client", f"{vid}"]})
            return resp

    def get_pf_openvpn_clients(self) -> dict:
        clients: list = []
        vpn_clients = self.get_openvpn_settings()
        if "error" in vpn_clients.keys():
            return vpn_clients

        locations: set = self.get_pf_openvpn_locations(vpn_clients)
        for vpnclient in vpn_clients["openvpn-client"]:
            clients.append(vpnclient["server_addr"])

        return {"clients": clients, "locations": list(locations)}

    def get_pf_openvpn_locations(self, vpn_clients: dict) -> set:
        """
        Parameters
        ----------
        vpn_clients : dict
            .
        """
        locations = set()
        for client in vpn_clients["openvpn-client"]:
            loc = is_vpn_address(client["server_addr"])
            if loc is not None:
                locations.add(loc[1].lower())
        return locations
