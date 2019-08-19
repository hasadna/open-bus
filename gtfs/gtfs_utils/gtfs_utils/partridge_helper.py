import datetime
import partridge as ptg


def get_partridge_filter_for_date(zip_path: str, date: datetime.date):
    service_ids = ptg.read_service_ids_by_date(zip_path)[date]

    return {
        'trips.txt': {
            'service_id': service_ids,
        },
    }


def get_partridge_feed_by_date(zip_path: str, date: datetime.date):
    return ptg.feed(zip_path, view=get_partridge_filter_for_date(zip_path, date))


def write_filtered_feed_by_date(zip_path: str, date: datetime.date, output_path: str):
    ptg.writers.extract_feed(zip_path, output_path, get_partridge_filter_for_date(zip_path, date))


