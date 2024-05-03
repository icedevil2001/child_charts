import re 

def get_extension_from_url(url: str) -> str:
    return re.search(r'\.(\w+)$', url).group(1)