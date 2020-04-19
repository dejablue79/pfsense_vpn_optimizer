Requires pfSense-pkg-FauxAPI

#### Endpoints

`http://localhost:5000/?q=pvpn&loc=dk`

q = pvpn | nvpn

Return recommended servers by provider and location.

```{
  "12": "dk-07.protonvpn.com", 
  "34": "dk-06.protonvpn.com", 
  "39": "dk-09.protonvpn.com", 
  "43": "dk-01.protonvpn.com", 
  "44": "dk-11.protonvpn.com", 
  "51": "dk-04.protonvpn.com", 
  "53": "dk-12.protonvpn.com", 
  "60": "dk-02.protonvpn.com", 
  "67": "dk-05.protonvpn.com", 
  "88": "dk-10.protonvpn.com", 
  "92": "dk-03.protonvpn.com", 
  "96": "dk-08.protonvpn.com"
}
```

`http://localhost:5000/get_settings`

Return List from current VPN clients settings

```
[
  "il35.nordvpn.com", 
  "us-ny-13.protonvpn.com", 
  "us5108.nordvpn.com", 
  "us-ny-09.protonvpn.com", 
  "de-16.protonvpn.com", 
  "de540.nordvpn.com", 
  "de-14.protonvpn.com"
]
```
`http://localhost:5000/comp`

Return JSON with current VPN setting and the recommended  servers.
```json
{
  "NordVPN": {
    "de": {
      "available_servers": {
        "14": "de775.nordvpn.com", 
        "16": "de695.nordvpn.com"
      }, 
      "pfsense": [
        "de540.nordvpn.com"
      ]
    }, 
    "us": {
      "available_servers": {
        "22": "us3268.nordvpn.com", 
        "24": "us5142.nordvpn.com"
      }, 
      "pfsense": [
        "us5108.nordvpn.com"
      ]
    } 
  }, 
  "protonVPN": {
    "de": {
      "available_servers": {
        "55": "de-12.protonvpn.com", 
        "58": "de-02.protonvpn.com", 
        "73": "de-10.protonvpn.com", 
        ...
      }, 
      "pfsense": [
        "de-16.protonvpn.com", 
        "de-14.protonvpn.com"
      ]
    },  
    "us": {
      "available_servers": {
        "46": "us-ny-11.protonvpn.com", 
        "48": "us-ny-17.protonvpn.com", 
        "56": "us-ny-06.protonvpn.com", 
        ...
      }, 
      "pfsense": [
        "us-ny-13.protonvpn.com", 
        "us-ny-09.protonvpn.com"
      ]
    }
  }
}

```
`http://localhost:5000/set`

Set vpn clients with recommended servers.       