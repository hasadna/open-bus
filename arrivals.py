import urllib2
import pytz
import traceback
from jinja2 import Environment, FileSystemLoader
from datetime import datetime


REQUEST_TEMPLATE_FILENAME = "request-template.xml"
REQUEST_TEMPLATE = Environment(loader=FileSystemLoader('.')).get_template(REQUEST_TEMPLATE_FILENAME)
HEADERS = {'Content-Type': 'text/xml; charset=utf-8'}
SIRI_SERVICES_URL = 'http://siri.motrealtime.co.il:8081/Siri/SiriServices'


def get_arrivals_response_xml(request_xml):
    """
    Args:
        request_xml - Siri request XML (String)
    Returns:
        Siri response XML (String)
    """
    try:
        req = urllib2.Request(SIRI_SERVICES_URL, headers=HEADERS, data=request_xml)
        res = urllib2.urlopen(req).read()
        return res
    except urllib2.URLError:
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
