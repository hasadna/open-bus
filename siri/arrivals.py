import urllib.request
import pytz
import traceback
from jinja2 import Environment, FileSystemLoader
from datetime import datetime


REQUEST_TEMPLATE_FILE = "request.template"
REQUEST_TEMPLATE = Environment(loader=FileSystemLoader('templates')).get_template(REQUEST_TEMPLATE_FILE)
HEADERS = {'Content-Type': 'text/xml; charset=utf-8'}
SIRI_SERVICES_URL = 'http://siri.motrealtime.co.il:8081/Siri/SiriServices'
HTTP_PROXY = 'http://openbus@192.241.154.128:5035'

def get_arrivals_response_xml(request_xml):
    """
    Args:
        request_xml - Siri request XML (String)
    Returns:
        Siri response XML (String)
    """
    try:
        proxy = urllib.request.ProxyHandler({'http': HTTP_PROXY})
        opener = urllib.request.build_opener(proxy)
        urllib.request.install_opener(opener)
        req = urllib.request.Request(SIRI_SERVICES_URL, headers=HEADERS, data=request_xml.encode('utf8'))
        res = urllib.request.urlopen(req).read()
        return res
    except urllib.request.URLError:
        traceback.print_exc()


def get_arrivals_request_xml(stops):
    """
    Args:
        stops - List of stop IDs
    Returns:
        Siri request XML (String)
    """
    timestamp = datetime.now(pytz.timezone("Israel")).isoformat()
    request_xml = REQUEST_TEMPLATE.render(stops=stops, timestamp=timestamp)
    return request_xml