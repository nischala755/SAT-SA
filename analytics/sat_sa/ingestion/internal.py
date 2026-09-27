"""Disabled-by-default, administrator-configured internal export adapter."""
import ipaddress
import json
from urllib.parse import urlsplit
from urllib.request import build_opener,ProxyHandler,HTTPRedirectHandler

def validate_endpoint(url):
    parsed=urlsplit(url)
    try: address=ipaddress.ip_address(parsed.hostname or '')
    except ValueError: raise ValueError('Internal export requires a literal private IP address') from None
    if parsed.scheme not in ('http','https') or parsed.username or parsed.password or parsed.fragment or not address.is_private or address.is_link_local or address.is_unspecified or address.is_multicast:
        raise ValueError('Invalid internal export endpoint')
    return url

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): raise ValueError('Internal export redirects are disabled')

def fetch_export(url):
    if not url: raise ValueError('Internal export adapter is disabled')
    validate_endpoint(url)
    try:
        with build_opener(ProxyHandler({}),NoRedirect()).open(url,timeout=10) as response: payload=response.read(2000001)
        if len(payload)>2000000: raise ValueError('Internal export exceeds 2 MB')
        result=json.loads(payload)
        if not isinstance(result,dict) or set(result)!={'files'}: raise ValueError('Internal export must contain a files array')
        return result
    except (OSError,json.JSONDecodeError) as exc: raise ValueError(f'Internal export unavailable ({type(exc).__name__})') from None
