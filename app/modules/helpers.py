import re
from typing import Match


def is_vpn_address(match: str) -> Match[str]:
    reg = rf"(\w\w).+?({str.join('|', get_providers())})\.com"
    return re.match(reg, match)


def is_supported_provider(provider: str) -> bool:
    return provider in get_providers()


def get_providers() -> set:
    return {"protonvpn", "nordvpn"}
