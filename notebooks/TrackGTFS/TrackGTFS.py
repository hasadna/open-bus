import pandas as pd


def find_gtfs_changes(gtfs_old, gtfs_new, col):

    ## col to dict of sets
    gtfs_old_dict = gtfs_old.groupby(gtfs_old.route_id)[col].agg(lambda i: i.str.split(';')).to_dict()
    gtfs_old_dict = {key: set(val) for key, val in gtfs_old_dict.items()}

    gtfs_new_dict = gtfs_new.groupby(gtfs_new.route_id)[col].agg(lambda i: i.str.split(';')).to_dict()
    gtfs_new_dict = {key: set(val) for key, val in gtfs_new_dict.items()}

    ## find_changes
    changes = {}

    all_routes = set(gtfs_old_dict.keys()) | set(gtfs_new_dict.keys())

    for route in all_routes:
        if route in gtfs_old_dict and route in gtfs_new_dict:
            if gtfs_new_dict[route] ^ gtfs_old_dict[route]:
                changes[route] = {}
                added = ";".join(gtfs_new_dict[route] - gtfs_old_dict[route])
                deleted = ";".join(gtfs_old_dict[route] - gtfs_new_dict[route])

                if added:
                    changes[route]['added'] = added
                if deleted:
                    changes[route]['deleted'] = deleted
        else:
            changes[route] = {}

            if route not in gtfs_new_dict:
                changes[route]['deleted'] = ";".join(gtfs_old_dict[route])

            elif route not in gtfs_old_dict:
                changes[route]['added'] = ";".join(gtfs_new_dict[route])

    ## set results as df & and add cols from gtfs_old & gtfs_new
    changes_df = pd.DataFrame.from_dict(changes, orient='index').reset_index().rename(columns={'index': 'route_id'})

    cols_to_import = ['agency_id', 'agency_name', 'route_short_name', 'route_long_name',
                      'start_stop_city', 'end_stop_city', 'date', col]

    changes_df = changes_df.merge(
        gtfs_old[['route_id'] + cols_to_import], on='route_id', how='left') \
        .rename(columns={c: f'{c}_old' for c in cols_to_import})

    changes_df = changes_df.merge(
        gtfs_new[['route_id'] + cols_to_import], on='route_id', how='left') \
        .rename(columns={c: f'{c}_new' for c in cols_to_import})

    return changes_df