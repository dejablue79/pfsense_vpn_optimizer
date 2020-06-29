import requests


class ProtonVPN:
    """
    ProtonVPN Thingy...
    ...
    Methods
    -------
    receive_servers_list(loc: str = None) -> dict
    """

    def __init__(self):
        self.base_url = "https://api.protonvpn.ch/vpn/logicals"
        self.location = "https://api.protonvpn.ch/vpn/location"
        self.tier = 2
        self.features = 0

    def receive_servers_list(self, loc: str = None) -> dict:
        data: dict = {}

        resp = requests.get(self.base_url)
        info = resp.json()
        for server in info["LogicalServers"]:
            if loc:
                if server["ExitCountry"] == loc.upper() \
                        and server["Tier"] == self.tier \
                        and server["Features"] == self.features \
                        and server["Status"] == 1:
                    if loc.upper() == "US" \
                            and server['City'] == 'New York City':
                        data[server["Domain"]] = int(server["Load"])
                    if loc.upper() == "DE" \
                            and server['City'] == 'Berlin':
                        data[server["Domain"]] = int(server["Load"])
                    elif loc.upper() != "US":
                        data[server["Domain"]] = int(server["Load"])
            else:
                data = resp["LogicalServers"]

        return {k: v for k, v in sorted(data.items(), key=lambda item: item[1])}