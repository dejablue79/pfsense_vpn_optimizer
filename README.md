### Pfsense_VPN_Optimizer
A docker container which builds a local webserver with an API for easier interaction with the pfsense-fauxapi package developed by @github/ndejong
in order to optimize NordVPN and ProtonVPN clients for single or multiple locations.
### Software Dependencies:

- pfSense v2.x
- [FauxAPI on pfsense](https://github.com/ndejong/pfsense_fauxapi)

To run without Docker:
- Python 3.X
- pip for python 3

```sh
pip3 install -r requirements.txt
```

With Docker compose:
```sh
docker-compose up --build
```
or with Docker:
```sh
docker run -e "HOST_ADDRESS=<HOST_ADDRESS>" -e "FAUXAPI_KEY=<FAUXAPI_KEY>" -e "FAUXAPI_SECRET=<FAUXAPI_SECRET>" -p 5000:5000 hva3lb9jp9fnn9cd8nay/pfsense_vpn_optimizer
```

### Configuration Prerequisite:

- You must have protonvpn and/or nordvpn configured and working on your pfsense server.
  - [ProtonVPN install guide](https://protonvpn.com/support/pfsense-vpn-setup/)
  - [NordVPN install guide](https://nordvpn.com/tutorials/pfsense/pfsense-openvpn/)
 
  for both providers, please use the *domain* *name* rather than the IP address for `Server host or address` 
- In order to use [function_call](https://github.com/ndejong/pfsense_fauxapi#user-content-function_call) uncomment this line `openvpn.inc:function openvpn_restart_by_vpnid($mode, $vpnid)`
### Endpoints

#### Recommended servers
Get recommended servers from ProtonVPN or NordVPN

    GET /?q=:provider&loc=:location

| Attribute     | Type   | Required | Description                                   |
|:------------- |:-------|:---------|:----------------------------------------------|
| provider      | string | yes      | protonvpn or nordvpn                          |
| location      | string | no       | ISO_3166-1_alpha-2 - Two letters country code |

```sh
curl "http://localhost:5000/?q=protonvpn&loc=dk"
```

Example of response

```json
{
  "dk-03.protonvpn.com": 66, 
  "dk-04.protonvpn.com": 69, 
  "dk-08.protonvpn.com": 47, 
  "dk-09.protonvpn.com": 36, 
  "dk-10.protonvpn.com": 28, 
  "dk-11.protonvpn.com": 34, 
  "dk-12.protonvpn.com": 30
}
```

#### Current clients settings
Get current VPN clients settings from pfSense
    
    GET /get_settings
```sh
curl "http://localhost:5000/get_settings"
```

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

#### Compare settings
Compare current VPN clients settings from pfSense and recommended servers 

    GET /compare
```sh
curl "http://localhost:5000/compare"
```

Example of response
```json
{
  "nordvpn": {
     "de": {
      "available_servers": {
        "de501.nordvpn.com": 11, 
        "de520.nordvpn.com": 11, 
        "de683.nordvpn.com": 10, 
        "de688.nordvpn.com": 10, 
        "de689.nordvpn.com": 12, 
        "de700.nordvpn.com": 10, 
        "de712.nordvpn.com": 11, 
        "de724.nordvpn.com": 11, 
        "de765.nordvpn.com": 7, 
        "de793.nordvpn.com": 11
      }, 
      "pfsense": {
        "de717.nordvpn.com": null, 
        "de740.nordvpn.com": null
      }
    }
  }, 
  "protonvpn": {
    "de": {
      "available_servers": {
        "de-03.protonvpn.com": 80, 
        "de-04.protonvpn.com": 100, 
        "de-10.protonvpn.com": 74, 
        "de-11.protonvpn.com": 81, 
        "de-12.protonvpn.com": 62, 
        "de-16.protonvpn.com": 66, 
        "de-17.protonvpn.com": 90, 
        "de-18.protonvpn.com": 63, 
        "de-19.protonvpn.com": 100, 
        "de-20.protonvpn.com": 46, 
        "de-24.protonvpn.com": 54, 
        "de-25.protonvpn.com": 69, 
        "de-26.protonvpn.com": 63, 
        "de-27.protonvpn.com": 55, 
        "de-28.protonvpn.com": 60
      }, 
      "pfsense": { 
        "de-19.protonvpn.com": 100, 
        "de-25.protonvpn.com": 69
      }
    },  
    "us": {
      "available_servers": {
        "us-ny-06.protonvpn.com": 44, 
        "us-ny-07.protonvpn.com": 44, 
        "us-ny-09.protonvpn.com": 47, 
        "us-ny-10.protonvpn.com": 54, 
        "us-ny-11.protonvpn.com": 92, 
        "us-ny-12.protonvpn.com": 50, 
        "us-ny-16.protonvpn.com": 100, 
        "us-ny-17.protonvpn.com": 44, 
        "us-ny-18.protonvpn.com": 58, 
        "us-ny-19.protonvpn.com": 51, 
        "us-ny-20.protonvpn.com": 100
      }, 
      "pfsense": {
        "us-ny-10.protonvpn.com": 54
      }
    }
  }
}
```

#### Set settings
Set vpn clients with recommended servers.

    GET /set
```sh
curl "http://localhost:5000/set"
```

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

#### Change location
Set recommended servers from ProtonVPN or NordVPN with different location

    GET /replace/:provider?loc=:old_location&with=:new_location

| Attribute     | Type   | Required | Description                                   |
|:------------- |:-------|:---------|:----------------------------------------------|
| provider      | string | yes      | protonvpn or nordvpn                          |
| old_location  | string | yes      | ISO_3166-1_alpha-2 - Two letters country code |
| new_location  | string | yes      | ISO_3166-1_alpha-2 - Two letters country code |

```sh
curl "http://localhost:5000/replace/nordvpn?loc=de&with=nl"
```
 
 To do
[ ] Change hardcoded US servers for ProtonVPN
[ ] Validate VPN locations for the `/replace` endpoint

