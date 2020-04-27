Requires pfSense-pkg-FauxAPI

#### Endpoints

`http://localhost:5000/?q=protonvpn&loc=dk`

q = protonvpn | nordvpn

Return recommended servers by provider and location.

```json
{
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

Return JSON from current VPN clients settings

```json
{
  "clients": [
    "de640.nordvpn.com", 
    "de-12.protonvpn.com", 
    "de-04.protonvpn.com", 
    "de543.nordvpn.com", 
    "us-ny-12.protonvpn.com"
  ], 
  "locations": [
    "de", 
    "us"
  ]
}
```
`http://localhost:5000/comp`

Return JSON with current VPN setting and the recommended  servers.
```json
{
  "nordvpn": {
    "de": {
      "available_servers": {
        "10": "de725.nordvpn.com", 
        "11": "de740.nordvpn.com"
      }, 
      "pfsense": [
        "de690.nordvpn.com", 
        "de703.nordvpn.com"
      ]
    }, 
    "us": {
      "available_servers": {
        "15": "us4729.nordvpn.com", 
        "18": "us4643.nordvpn.com", 
        "20": "us3391.nordvpn.com"
      }, 
      "pfsense": []
    }
  }, 
  "protonvpn": {
    "de": {
      "available_servers": {
        "31": "de-10.protonvpn.com", 
        "38": "de-26.protonvpn.com", 
        "48": "de-28.protonvpn.com", 
        "56": "de-04.protonvpn.com", 
        "57": "de-11.protonvpn.com", 
        "71": "de-24.protonvpn.com", 
        "84": "de-25.protonvpn.com", 
        "86": "de-12.protonvpn.com", 
        "100": "de-27.protonvpn.com"
      }, 
      "pfsense": [
        "de-18.protonvpn.com", 
        "de-17.protonvpn.com"
      ]
    }, 
    "us": {
      "available_servers": {
        "41": "us-ny-18.protonvpn.com", 
        "52": "us-ny-07.protonvpn.com", 
        "53": "us-ny-17.protonvpn.com", 
        "55": "us-ny-09.protonvpn.com", 
        "59": "us-ny-10.protonvpn.com", 
        "65": "us-ny-20.protonvpn.com", 
        "75": "us-ny-19.protonvpn.com", 
        "85": "us-ny-11.protonvpn.com", 
        "91": "us-ny-12.protonvpn.com"
      }, 
      "pfsense": [
        "us-ny-07.protonvpn.com"
      ]
    }
  }
}
```
`http://localhost:5000/set`

Set vpn clients with recommended servers.

Return:

```json
{
  "info": {
    "action": "config_set", 
    "callid": "5ea6d1cfacc06", 
    "data": {
      "do_backup": true, 
      "do_reload": true, 
      "previous_config_file": "/cf/conf/backup/config-1587990991.xml"
    }, 
    "message": "ok"
  }, 
  "nordvpn": {
    "new": {
      "de": [
        "de690.nordvpn.com", 
        "de703.nordvpn.com"
      ]
    }, 
    "old": {
      "de": [
        "de768.nordvpn.com", 
        "de690.nordvpn.com"
      ]
    }
  }, 
  "protonvpn": {
    "new": {
      "de": [
        "de-18.protonvpn.com", 
        "de-17.protonvpn.com"
      ]
    }, 
    "old": {
      "de": [
        "de-17.protonvpn.com", 
        "de-18.protonvpn.com"
      ]
    }
  }
}
``` 
or
```json
{
  "nordvpn": "No Need to Update", 
  "protonvpn": "No Need to Update"
}
```