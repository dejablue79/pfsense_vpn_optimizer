import re
from typing import Match


def is_vpn_address(match: str) -> Match[str]:
    reg = r"(\w\w).+?(protonvpn|nordvpn)\.com"
    return re.match(reg, match)


def is_supported_provider(provider: str) -> bool:
    return provider in get_providers()


def get_providers() -> set:
    return {"protonvpn", "nordvpn"}
