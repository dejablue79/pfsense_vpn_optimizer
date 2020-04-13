Requires pfSense-pkg-FauxAPI

#### Endpoints
    /?q=[]&loc=[]
q = pvpn|nvpn

Return recommanded servers by provider and location. 
http://localhost:5000/?q=pvpn&loc=dk
 

     /comp
Return JSON with current VPN setting and the recommanded servers.


    /get_settings
Retun JSON from current VPN clients settings



    /set
Set vpn clients with recommanded servers.