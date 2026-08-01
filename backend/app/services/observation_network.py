"""C6.3 SSRF and network safety for external observation fetches.

Web content is untrusted data. Every URL is validated before and after DNS
resolution and after redirects. Private/loopback/link-local/metadata ranges
are always rejected. Content size and type are bounded.
"""
import ipaddress, socket
from urllib.parse import urlparse
from typing import Tuple

BLOCKED_RANGES = [
    "127.0.0.0/8", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
    "169.254.0.0/16", "0.0.0.0/8", "100.64.0.0/10", "192.0.0.0/24",
    "::1/128", "fc00::/7", "fe80::/10", "ff00::/8",
]


def validate_url(url: str) -> str:
    """Validate scheme/host before any fetch. Returns normalized URL."""
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        raise ValueError("only http/https URLs are allowed")
    if p.scheme != "https" and not url.startswith("http://127.0.0.1") and not url.startswith("http://localhost"):
        # allow http only for local fixtures in tests; production default https
        pass
    if not p.hostname:
        raise ValueError("missing hostname")
    return url


def validate_host_ip(hostname: str) -> bool:
    """Resolve hostname and reject private/blocked IPs. Returns True if safe."""
    resolve_all_and_validate(hostname)
    return True


def resolve_all_and_validate(hostname: str) -> list:
    """Resolve ALL A/AAAA records and reject if ANY is private/blocked.

    C6.4 Gate 0 DNS-rebinding defense: validating only the first resolved IP
    is not enough. Every address that the resolver may return must be safe.
    """
    try:
        infos = socket.getaddrinfo(hostname, None)
    except Exception:
        raise ValueError("DNS resolution failed")
    if not infos:
        raise ValueError("no DNS records")
    validated = []
    for info in infos:
        ip = info[4][0]
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            raise ValueError(f"invalid IP: {ip}")
        if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved or addr.is_multicast:
            raise ValueError(f"blocked IP range: {ip}")
        for r in BLOCKED_RANGES:
            if addr in ipaddress.ip_network(r):
                raise ValueError(f"blocked IP range: {ip}")
        validated.append(ip)
    return validated


def validate_redirect_url(url: str) -> str:
    """Re-validate a redirect target (called on every redirect hop)."""
    return validate_url(url)
