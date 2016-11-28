from collections import namedtuple
import xml.etree.ElementTree as ET

import re
import logging as lg

# these are all the possible fields according to the documentation
# many of them are usually not supplied (never supplied?)
monitored_stop_visit_fields = ['recorded_at_time', 'item_identifier', 'monitoring_ref',
                               'line_ref', 'direction_ref',
                               'operator_ref', 'published_line_name', 'destination_ref', 'dated_vehicle_journey_ref',
                               'vehicle_ref', 'confidence_level', 'origin_aimed_departure_time', 'stop_point_ref',
                               'vehicle_at_stop', 'request_stop', 'destination_display', 'aimed_arrival_time',
                               'actual_arrival_time', 'expected_arrival_time', 'arrival_status',
                               'arrival_platform_name', 'arrival_boarding_activity',
                               'actual_departure_time', 'aimed_departure_time', 'stop_visit_note']

MonitoredStopVisit = namedtuple('MonitoredStopVisit', monitored_stop_visit_fields)


def parse_siri_reply(raw_xml, request_id=-1):
    """Parses the reply and returns a list of MonitoredStopVisit instances"""

    def remove_namespace_elements(s):
        return re.sub('<(/?)\w+:([^>]+)>', r'<\1\2>', s)

    def optional(e, child_tag, default=''):
        child = e.find(child_tag)
        return child.text if child is not None else default

    def to_snake_case(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def log_unexpected_children(el, el_id, expected_children):
        unexpected_tags = [e.tag for e in el.getchildren() if e.tag not in expected_children]
        if unexpected_tags:
            lg.warning("Unexpected children %s found (request %s MonitoredStopVisit %s)" % (unexpected_tags,
                                                                                            request_id, el_id))

    def build_data(el, fields):
        return {to_snake_case(field_name): optional(el, field_name) for field_name in fields}

    def element_to_msv(msv_el, el_id):
        msv_fields = {'RecordedAtTime', 'ItemIdentifier', 'MonitoringRef'}
        mvj_fields = {'LineRef', 'DirectionRef', 'OperatorRef', 'PublishedLineName', 'DestinationRef',
                      'DatedVehicleJourneyRef', 'VehicleRef', 'ConfidenceLevel', 'OriginAimedDepartureTime'}
        mc_fields = {'StopPointRef', 'VehicleAtStop', 'RequestStop', 'DestinationDisplay',
                     'AimedArrivalTime', 'ActualArrivalTime', 'ExpectedArrivalTime',
                     'ArrivalStatus', 'ArrivalPlatformName', 'ArrivalBoardingActivity',
                     'ActualDepartureTime', 'AimedDepartureTime'}

        # get required children elements
        mvj_el = msv_el.find('MonitoredVehicleJourney')
        if not mvj_el:
            lg.info('MonitoredVehicleJourney element missing (request %s MonitoredStopVisit %s)' % (request_id, el_id))
            return

        mc_el = mvj_el.find('MonitoredCall')
        if not mc_el:
            lg.info('MonitoredCall element missing (request %s, MonitoredStopVisit %s)' % (request_id, el_id))
            return

        # unexpected children may mean there's a problem with the parsing,
        log_unexpected_children(msv_el, el_id, msv_fields.union(['MonitoredVehicleJourney', 'StopVisitNote']))
        log_unexpected_children(mvj_el, el_id, mvj_fields.union(['MonitoredCall']))
        log_unexpected_children(mc_el, el_id, mc_fields)

        data = build_data(msv_el, msv_fields)
        data.update(build_data(mvj_el, mvj_fields))
        data.update(build_data(mc_el, mc_fields))
        # notes gets special treatment because in theory there can be any number of notes
        data['stop_visit_note'] = ';'.join(stop_visit_note_el.text for stop_visit_note_el
                                           in msv_el.findall('StopVisitNote'))

        # fix booleans
        data['vehicle_at_stop'] = True if data['vehicle_at_stop'] == 'true' else False
        data['request_stop'] = True if data['request_stop'] == 'true' else False
        # fix times
        time_fields = ['origin_aimed_departure_time', 'aimed_arrival_time', 'actual_arrival_time',
                       'actual_departure_time', 'aimed_departure_time']
        for field in time_fields:
            data[field] = data[field] if data[field] != '' else None

        return MonitoredStopVisit(**data)

    x = ET.fromstring(remove_namespace_elements(raw_xml))
    msv_elements = (e for e in x.iter() if e.tag == 'MonitoredStopVisit')
    msv_with_nones = (element_to_msv(el, el_id) for (el_id, el) in enumerate(msv_elements))
    msv = (msv for msv in msv_with_nones if msv)  # remove None results
    return list(msv)
