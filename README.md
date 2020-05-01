### Pfsense_VPN_Optimizer
A docker container which builds a local webserver with an API for easier interaction with the pfsense-fauxapi package developed by ndejong

### Software Dependencies:

pfSense v2.x

[FauxAPI on pfsense](https://github.com/ndejong/pfsense_fauxapi) 

Python 3.X

Pip for python 3

pfsense-fauxapi python library:

    pip3 install pfsense-fauxapi

### Configuration Prerequisite:

You must have protonvpn and/or nordvpn configured and working on your pfsense server.

ProtonVPN install guide: https://protonvpn.com/support/pfsense-vpn-setup/

NordVPN install guide: https://nordvpn.com/tutorials/pfsense/pfsense-openvpn/

#### Endpoints

##### Recommended servers
Get recommended servers from ProtonVPN or NordVPN

    GET /?q=:provider&loc=:location

| Attribute     | Type   | Required | Description                                   |
| ------------- |--------|----------|-----------------------------------------------|
| provider      | string | yes      | protonvpn or nordvpn                          |
| location      | string | no       | ISO_3166-1_alpha-2 - Two letters country code |


    curl "http://localhost:5000/?q=protonvpn&loc=dk"

Example of response

```json
{
  "18": "dk-12.protonvpn.com",
  "23": "dk-10.protonvpn.com",
  "29": "dk-08.protonvpn.com",
  "31": "dk-09.protonvpn.com",
  "59": "dk-03.protonvpn.com"
}
```

##### Current clients settings
Get current VPN clients settings from pfSense
    
    GET /get_settings
    curl "http://localhost:5000/get_settings"

Example of response
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

##### Compare settings
Compare current VPN clients settings from pfSense and recommended servers 

    GET /comp
    curl "http://localhost:5000/comp"

Example of response
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
##### Set settings
Set vpn clients with recommended servers.

    GET /set
    http://localhost:5000/set

Example of response
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
Example of response when update is not needed
```json
{
  "nordvpn": "No Need to Update", 
  "protonvpn": "No Need to Update"
}
```