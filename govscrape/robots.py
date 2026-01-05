from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

_robot_cache = {}

def allowed_by_robots(url: str, user_agent: str) -> bool:
    """
    Basic robots.txt gate. If robots.txt cannot be fetched, we default to ALLOW
    but you can flip that behavior if you want stricter rules.
    """
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{base}/robots.txt"

    rp = _robot_cache.get(robots_url)
    if rp is None:
        rp = RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
        except Exception:
            # If robots can't be read, we choose to allow (common research behavior).
            # You can change to return False for stricter compliance.
            _robot_cache[robots_url] = rp
            return True
        _robot_cache[robots_url] = rp

    return rp.can_fetch(user_agent, url)
