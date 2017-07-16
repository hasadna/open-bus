from collections import namedtuple
import xml.etree.ElementTree as ET

import re
import logging as lg

# these are unused fields: (see https://github.com/hasadna/open-bus/blob/f7de04d88eab183a277d5fc3ae6f459d47ea8545/doc/db_tables.md)
# if you wish to add them make sure to change the code and DB accordingly
unused_fields = ['request_stop', 'destination_display',
                 'actual_arrival_time',  'arrival_status',
                 'arrival_platform_name', 'arrival_boarding_activity',
                 'actual_departure_time', 'aimed_departure_time', 'stop_visit_note',
                 'confidence_level']

# these are the extracted fields:
monitored_stop_visit_fields = ['recorded_at_time', 'item_identifier', 'monitoring_ref',
                               'line_ref', 'direction_ref',
                               'operator_ref', 'published_line_name', 'destination_ref', 'dated_vehicle_journey_ref',
                               'vehicle_ref', 'origin_aimed_departure_time', 'stop_point_ref',
                               'vehicle_at_stop', 'aimed_arrival_time',
                                'expected_arrival_time', 'vehicle_location_lat', 'vehicle_location_lon']


MonitoredStopVisit = namedtuple('MonitoredStopVisit', monitored_stop_visit_fields)


def parse_siri_reply(raw_xml, request_id=-1):
    """Parses the reply and returns a list of MonitoredStopVisit instances"""

    def remove_namespace_elements(s):
        return re.sub('<(/?)\w+:([^>]+)>', r'<\1\2>', s)

    def optional(parent_element, child_tag, default=''):
        if parent_element is None:
            return default
        child = parent_element.find(child_tag)
        return child.text if child is not None else default

    def to_snake_case(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def log_unexpected_children(el, el_id, expected_children):
        unexpected_tags = [e.tag for e in el.getchildren() if e.tag not in expected_children]
        if unexpected_tags:
            lg.warning("Unexpected children %s found (request %s MonitoredStopVisit %s)" % (unexpected_tags,
                                                                                            request_id, el_id))

    def extract_children(el, children):
        """Extracts the given children from the parent element. Returns a map from the child name in snake case,
        to the child element value. If the child is missing, returns empty string for that child.
        """
        return {to_snake_case(child): optional(el, child) for child in children}

    def extract_location(mvj_el):
        location_el = mvj_el.find('VehicleLocation')
        # convert location fields into float and round.
        vehicle_location_lat = optional(location_el, 'Latitude')[:18]
        vehicle_location_lon = optional(location_el, 'Longitude')[:18]
        return {'vehicle_location_lat': round(float(vehicle_location_lat),5) if vehicle_location_lat != '' else None,
                'vehicle_location_lon':  round(float(vehicle_location_lon),5) if vehicle_location_lon != '' else None}

    def element_to_msv(msv_el, el_id):
        msv_fields = {'RecordedAtTime', 'ItemIdentifier', 'MonitoringRef'}
        mvj_fields = {'LineRef', 'DirectionRef', 'OperatorRef', 'PublishedLineName', 'DestinationRef',
                      'DatedVehicleJourneyRef', 'VehicleRef', 'OriginAimedDepartureTime'}
        mc_fields = {'StopPointRef', 'VehicleAtStop',
                     'AimedArrivalTime', 'ExpectedArrivalTime'}

        # get required children elements
        mvj_el = msv_el.find('MonitoredVehicleJourney')
        if not mvj_el:
            lg.info('MonitoredVehicleJourney element missing (request %s MonitoredStopVisit %s)' % (request_id, el_id))
            return

        mc_el = mvj_el.find('MonitoredCall')
        if not mc_el:
            lg.info('MonitoredCall element missing (request %s, MonitoredStopVisit %s)' % (request_id, el_id))
            return

        # unexpected children mean there are new fields we were not expecting, it's worth checking what they are
        log_unexpected_children(msv_el, el_id, msv_fields.union(['MonitoredVehicleJourney', 'StopVisitNote']))
        log_unexpected_children(mvj_el, el_id, mvj_fields.union(['MonitoredCall', 'VehicleLocation']))
        log_unexpected_children(mc_el, el_id, mc_fields)

        data = extract_children(msv_el, msv_fields)
        data.update(extract_children(mvj_el, mvj_fields))
        data.update(extract_children(mc_el, mc_fields))
        # Location gets a special treatment because it has two children nodes
        data.update(extract_location(mvj_el))
        # notes gets special treatment because in theory there can be any number of notes - currently not used
        # data['stop_visit_note'] = ';'.join(stop_visit_note_el.text for stop_visit_note_el
        #                                    in msv_el.findall('StopVisitNote'))

        # fix booleans
        data['vehicle_at_stop'] = True if data['vehicle_at_stop'] == 'true' else False
        # data['request_stop'] = True if data['request_stop'] == 'true' else False # currently not used
        # fix times
        time_fields = ['origin_aimed_departure_time','aimed_arrival_time']
        for field in time_fields:
            data[field] = data[field] if data[field] != '' else None

        return MonitoredStopVisit(**data)

    x = ET.fromstring(remove_namespace_elements(raw_xml))
    msv_elements = (e for e in x.iter() if e.tag == 'MonitoredStopVisit')
    msv_with_nones = (element_to_msv(el, el_id) for (el_id, el) in enumerate(msv_elements))
    msv = (msv for msv in msv_with_nones if msv)  # remove None results
    return list(msv)
