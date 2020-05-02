### Pfsense_VPN_Optimizer
A docker container which builds a local webserver with an API for easier interaction with the pfsense-fauxapi package developed by @github/ndejong

### Software Dependencies:

pfSense v2.x

[FauxAPI on pfsense](https://github.com/ndejong/pfsense_fauxapi) 

To run without Docker:
- Python 3.X
- Pip for python 3


    pip3 install -r requirements.txt

Or with Docker:

    docker-compose up --build

### Configuration Prerequisite:

You must have protonvpn and/or nordvpn configured and working on your pfsense server.

ProtonVPN install guide: https://protonvpn.com/support/pfsense-vpn-setup/

NordVPN install guide: https://nordvpn.com/tutorials/pfsense/pfsense-openvpn/

### Endpoints

#### Recommended servers
Get recommended servers from ProtonVPN or NordVPN

    GET /?q=:provider&loc=:location

| Attribute     | Type   | Required | Description                                   |
|:------------- |:-------|:---------|:----------------------------------------------|
| provider      | string | yes      | protonvpn or nordvpn                          |
| location      | string | no       | ISO_3166-1_alpha-2 - Two letters country code |


    curl "http://localhost:5000/?q=protonvpn&loc=dk"

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

#### Compare settings
Compare current VPN clients settings from pfSense and recommended servers 

    GET /comp
    curl "http://localhost:5000/comp"

Example of response
```json
{
  "nordvpn": {
    "de": {
      "available_servers": {
        "de487.nordvpn.com": 17, 
        "de496.nordvpn.com": 15, 
        "de527.nordvpn.com": 14, 
        "de532.nordvpn.com": 16, 
        "de552.nordvpn.com": 18, 
        "de597.nordvpn.com": 13, 
        "de647.nordvpn.com": 19, 
        "de695.nordvpn.com": 19, 
        "de755.nordvpn.com": 17, 
        "de778.nordvpn.com": 18
      }, 
      "pfsense": [
        "de763.nordvpn.com", 
        "de559.nordvpn.com"
      ]
    }, 
    "us": {
      "available_servers": {
        "us3039.nordvpn.com": 23, 
        "us3100.nordvpn.com": 23, 
        "us3397.nordvpn.com": 21, 
        "us4081.nordvpn.com": 24, 
        "us4320.nordvpn.com": 23, 
        "us4594.nordvpn.com": 24, 
        "us5132.nordvpn.com": 23, 
        "us5150.nordvpn.com": 20, 
        "us5169.nordvpn.com": 24, 
        "us5187.nordvpn.com": 22
      }, 
      "pfsense": []
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
      "pfsense": [
        "de-19.protonvpn.com", 
        "de-25.protonvpn.com"
      ]
    },  
    "us": {
      "available_servers": {
        "us-ny-06.protonvpn.com": 52, 
        "us-ny-07.protonvpn.com": 53, 
        "us-ny-09.protonvpn.com": 74, 
        "us-ny-10.protonvpn.com": 48, 
        "us-ny-11.protonvpn.com": 97, 
        "us-ny-12.protonvpn.com": 70, 
        "us-ny-16.protonvpn.com": 54, 
        "us-ny-17.protonvpn.com": 71, 
        "us-ny-18.protonvpn.com": 66, 
        "us-ny-19.protonvpn.com": 69, 
        "us-ny-20.protonvpn.com": 42
      }, 
      "pfsense": [
        "us-ny-20.protonvpn.com"
      ]
    }
  }
}

```
#### Set settings
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
#### Change location
Set recommended servers from ProtonVPN or NordVPN with different location

    GET /replace/:provider?loc=:old_location&with=:new_location

| Attribute     | Type   | Required | Description                                   |
|:------------- |:-------|:---------|:----------------------------------------------|
| provider      | string | yes      | protonvpn or nordvpn                          |
| old_location  | string | yes      | ISO_3166-1_alpha-2 - Two letters country code |
| new_location  | string | yes      | ISO_3166-1_alpha-2 - Two letters country code |
    
    curl "http://localhost:5000/replace/nordvpn?loc=de&with=nl"