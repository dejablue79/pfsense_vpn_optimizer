from PfsenseFauxapi.PfsenseFauxapi import PfsenseFauxapi, PfsenseFauxapiException
from os import getenv
import re


class PfSense:
    """
    A class used to represent an Animal

    ...

    Attributes
    ----------
    says_str : str
        a formatted string to print out what the animal says
    name : str
        the name of the animal
    sound : str
        the sound that the animal makes
    num_legs : int
        the number of legs the animal has (default 4)

    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes
    """
    def __init__(self):
        self.host = getenv("HOST_ADDRESS")
        self.port = 443
        self.key = getenv("FAUXAPI_KEY")
        self.secret = getenv("FAUXAPI_SECRET")
        self.reg = r"(\w\w).+?(protonvpn|nordvpn)\.com"

        self.pfapi = PfsenseFauxapi(f"{self.host}:{self.port}", self.key, self.secret)

    def get_openvpn_settings(self) -> dict:
        """
        Parameters
        ----------
        name : str
            The name of the animal
        sound : str
            The sound the animal makes
        num_legs : int, optional
            The number of legs the animal (default is 4)
        """
        try:
            pf_openvpn_settings = self.pfapi.config_get('openvpn')
        except PfsenseFauxapiException as e:
            return {"error": str(e)}
        else:
            return pf_openvpn_settings

    def set_pfsense_config(self, data: dict, vpnid: list, refresh: bool = None) -> dict:
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
        else:
            locations: set = self.get_pf_openvpn_locations(vpn_clients)

            for vpnclient in vpn_clients["openvpn-client"]:
                clients.append(vpnclient["server_addr"])
            return {"clients": clients, "locations": list(locations)}

    def get_pf_openvpn_locations(self, vpn_clients: dict) -> set:
        locations = set()
        for client in vpn_clients["openvpn-client"]:
            loc = re.match(self.reg, client["server_addr"])
            if loc is not None:
                locations.add(loc[1].lower())
        return locations
