import logging
import pandas as pd
from .configuration import configuration


def save_trip_stats(ts: pd.DataFrame,
                    output_path: str,
                    output_file_type: str = configuration.files.output_file_type) -> None:
    logging.info(f'Saving trip stats result DF to {output_path}')
    save_dataframe_to_file(ts, output_path, output_file_type)


def save_route_stats(rs: pd.DataFrame,
                     output_path: str,
                     output_file_type: str = configuration.files.output_file_type) -> None:
    logging.info(f'Saving route stats result DF to {output_path}')
    save_dataframe_to_file(rs, output_path, output_file_type)


def save_dataframe_to_file(df: pd.DataFrame,
                           output_path: str,
                           output_file_type: str = configuration.files.output_file_type) -> None:
    output_path = f'{output_path}.{output_file_type}'
    if output_file_type == 'pkl.gz':
        df.to_pickle(output_path, compression='gzip')
    elif output_file_type == 'csv.gz':
        df.to_csv(output_path, compression='gzip')
