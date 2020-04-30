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

## Installation

Pull down the repository:

    git clone https://github.com/dejablue79/pfsense_VPN_optimizer.git

Navigate inside the folder created:

    cd pfsense_VPN_optimizer/

Modify the docker-compse.yml file to match your environment:

```
environment:
      - fauxapi-secret=[CHANGE]
      - fauxapi-key=[CHANGE]
      - host-address=[CHANGE]
      - host-port=[CHANGE]
```

Update the secret and key variables with your pfSense-fauxAPI key and secret that you would have generated in the steps to installing the faux-api from https://github.com/ndejong/pfsense_fauxapi

Update the host-address variable with either your pfsense server's ip address or hostname as it will work with either. Update the host-port with the listening port of your pfsense server, this will depend on how you have your web configurator set up. 

For example:
80 is the default listening port for the http web configurator and 443 is the default listening port for the https web configurator. You can also specify a custom listening port when setting up the web configurator in the Advanced settings and would need to make sure that is in the docker-compse.yml file

Make sure you are in the directory with the Dockerfile and run the following

    docker-compose up -d

This will build the image and start the container for you

#### Endpoints

`http://localhost:5000/?q=protonvpn&loc=dk`

The 'q' variable can be either "protonvpn" or "nordvpn" depending on which you use on your server. 'loc' is how you set the location that you want to pull servers for from you respective provider.

Example return recommended servers by provider (protonvpn) and location (dk).

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

Example return JSON from current VPN clients settings

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

Example return JSON with current VPN setting and the recommended servers.

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

Example return:

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