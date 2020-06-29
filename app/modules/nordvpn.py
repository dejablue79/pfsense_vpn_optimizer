import requests


class NordVPN:
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
            r = requests.get(self.countries_url)
            countries = r.json()
            for country in countries:
                if country["code"] == loc.upper():
                    url = '&filters={"country_id":' + str(country["id"]) + '}'
                    r = requests.get(self.base_url + url)
                    resp = r.json()

        else:
            r = requests.get(self.base_url)
            resp = r.json()

        for server in resp:
            if server["status"] == "online":
                data[server["hostname"]] = int(server["load"])

        return {k: v for k, v in sorted(data.items(), key=lambda item: item[1])}