import logging


def save_trip_stats(ts: pd.DataFrame, output_path: str):
    logging.info(f'Saving trip stats result DF to gzipped pickle {output_path}')
    ts.to_pickle(output_path, compression='gzip')


def save_route_stats(rs: pd.DataFrame, output_path: str):
    logging.info(f'Saving route stats result DF to gzipped pickle {output_path}')
    rs.to_pickle(output_path, compression='gzip')
