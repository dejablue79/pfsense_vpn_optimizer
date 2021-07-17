import requests
from json import JSONDecodeError


class NordVPN:
    """
    NordVPN Thingy...
    ...
    Methods
    -------
    receive_servers_list(loc: str = None) -> dict
    """
    def __init__(self):
        self.base_url = "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations&limit=10"
        self.countries_url = "https://api.nordvpn.com/v1/servers/countries"
        self.tier = 2
        self.features = 0

    def receive_servers_list(self, loc: str = None) -> dict:
        data: dict = {}
        resp: dict = {}

        if loc is not None:
            if loc == "uk":
                loc = "gb"
            try:
                r = requests.get(self.countries_url)
            except requests.exceptions.RequestException as e:
                print(f"HTTP Code: {r.status_code}  {e}")
            else:
                try:
                    countries = r.json()
                except JSONDecodeError:
                    print(f"Invalid response: {r.text}")
                else:
                    for country in countries:
                        if country["code"] == loc.upper():
                            url = '&filters={"country_id":' + str(country["id"]) + '}'
                            try:
                                r = requests.get(self.base_url + url)
                            except requests.exceptions.RequestException as e:
                                print(f"HTTP Code: {r.status_code}  {e}")
                            else:
                                try:
                                    resp = r.json()
                                except JSONDecodeError:
                                    print(f"Invalid response: {r.text}")

        else:
            try:
                r = requests.get(self.base_url)
            except requests.exceptions.RequestException as e:
                print(f"HTTP Code: {r.status_code}  {e}")
            else:
                try:
                    resp = r.json()
                except JSONDecodeError:
                    print(f"Invalid response: {r.text}")

        for server in resp:
            if server["status"] == "online":
                data[server["hostname"]] = int(server["load"])

        return {k: v for k, v in sorted(data.items(), key=lambda item: item[1])}
