from bs4 import BeautifulSoup


class BusArrival(object):

    def __init__(self,
                 line_ref,
                 direction_ref,
                 published_line_name,
                 operator_ref,
                 destination_ref,
                 monitoring_ref,
                 expected_arrival_time,
                 stop_point_ref,
                 response_timestamp,
                 recorded_at,
                 response_xml):
        self.line_ref = line_ref
        self.direction_ref = direction_ref
        self.published_line_name = published_line_name
        self.operator_ref = operator_ref
        self.destination_ref = destination_ref
        self.monitoring_ref = monitoring_ref
        self.expected_arrival_time = expected_arrival_time
        self.stop_point_ref = stop_point_ref
        self.response_timestamp = response_timestamp
        self.recorded_at = recorded_at
        self.response_xml = response_xml

    def __str__(self):
        return "BusArrival<%s, %s, %s, %s, %s, %s, %s, %s, %s, %s>" % \
            (self.line_ref,
               self.direction_ref,
               self.published_line_name,
               self.operator_ref,
               self.destination_ref,
               self.monitoring_ref,
               self.expected_arrival_time,
               self.stop_point_ref,
               self.response_timestamp,
               self.recorded_at)


def _get_tag_text(tag):
    """
        Description:
            Helper method to extract text
            out of bs4 elements
        Args:
            tag - bs4 element
        Returns:
            its inner text if not None
            otherwise an empty string
    """
    return tag.getText() if tag is not None else ""


def _bus_node_to_busarrival_obj(bus_node,  response_xml):
    """
        Args:
            bus_node - an object taken from Siri XML
                       ("MonitoredStopVisit") using bs4

        Returns:
            An object of type BusArrival with all the necessary information
            taken from the given bus_node (bs4) object
    """
    if bus_node is not None:
        response_timestamp = bus_node.parent.ResponseTimestamp.getText()
        published_line_name = bus_node.PublishedLineName.getText()
        operator_ref = bus_node.OperatorRef.getText()
        monitoring_ref = bus_node.MonitoringRef.getText()
        expected_arrival_time = bus_node.ExpectedArrivalTime.getText()
        stop_point_ref = bus_node.StopPointRef.getText()
        direction_ref = bus_node.DirectionRef.getText()
        destination_ref = bus_node.DestinationRef.getText()
        line_ref = _get_tag_text(bus_node.LineRef)
        recorded_at = _get_tag_text(bus_node.RecordedAtTime)
        return BusArrival(line_ref,
                          direction_ref,
                          published_line_name,
                          operator_ref,
                          destination_ref,
                          monitoring_ref,
                          expected_arrival_time,
                          stop_point_ref,
                          response_timestamp,
                          recorded_at,
                          response_xml)


def parse_siri_xml(response_xml):
    """
    Args:
        response_xml - Siri response xml (String)

    Returns:
        List of BusArrival objects
    """

    soup = BeautifulSoup(response_xml, "xml")

    errors = soup.find_all("ErrorCondition")  # irrelevant ATM
    buses = soup.find_all("MonitoredStopVisit")
    return [_bus_node_to_busarrival_obj(bus, response_xml) for bus in buses]
