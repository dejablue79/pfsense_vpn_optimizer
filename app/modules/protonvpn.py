import requests


class ProtonVPN:
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
        self.base_url = "https://api.protonvpn.ch/vpn/logicals"
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