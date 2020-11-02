# imports
import sys
import pandas as pd
from io import BytesIO
from time import sleep, time

if 'splunk-sdk-python-1.6.6' not in sys.path:
    try:
        sys.path.append('splunk-sdk-python-1.6.6')
    except:
        None

import splunklib.client as client

#################################### splunk_query_builder ##################################################

def splunk_query_builder(**query_kwargs):
    '''This function creates Search Processing Language (SPL) query for Splunk database.

    Kwargs:
        columns (list): columns to select in the query. If None, select all columns.
        max_columns (int): maximum number of rows in the query. If None, the query will have no rows limitation.

        Additional kwargs for filtering by column value.
        Note that query filter order is based on this kwargs order, except for the indexes of "index", "earliest" & "latest".

    Returns:
        String: The SPL query.
    '''

    # transform query_kwargs to params and hyperparams
    hyperparams = ['max_columns', 'columns']

    indexes_order = ['index', 'earliest', 'latest']

    params = [param for param in indexes_order if param in query_kwargs.keys()] + \
             [param for param in query_kwargs.keys() if param not in indexes_order and param not in hyperparams]

    # filter rows ("where")
    query = "search "

    where_list = []

    for param in params:
        if query_kwargs[param]:
            if isinstance(query_kwargs[param], (list, tuple,dict, set)):
                print("can't filter by list ({})\n".format(param))
            else:
                where_list.append('{}={} '.format(param, query_kwargs[param]))

    if where_list:
        query = query + "".join(where_list) + '|'

    else:
        query = query + ' *|'

    # filter columns ("select")
    if 'columns' in query_kwargs and isinstance(query_kwargs['columns'], list):
        query = query + " fields " + ", ".join(query_kwargs['columns']) + " |"
    else:
        query = query + ' fields * |'

    # cut rows ("top")
    if 'max_columns' in query_kwargs:
        query = query + ' head {}'.format(query_kwargs['max_columns'])

    return query

############################################ read_splunk ################################################

def read_splunk(query, username, password, host, port, time_limit=5):
    '''This function queries Splunk database.
    Note that function dependencies includes installing splunklib.

    Args:
        query (str): SPL query.
        username (str): Splunk username.
        password (str): Splunk password.
        host (str): Splunk host.
        port (int): Splunk management port.
        time_limit (int): time limit (minutes) for the query (default: 5).

    Returns:
        DataFrame: query results.
    '''

    # save start time
    start_time = time()

    print('start..\n')

    print('your query:\n {}\n'.format("|\n".join(query.split("|"))))

    # connect to splunk
    service = client.connect(host=host, port=port, username=username, password=password)
    print('connection succeed\n')

    # query splunk
    kwargs_normalsearch = {"exec_mode": "normal", "count": 0}
    job = service.jobs.create(query, **kwargs_normalsearch)

    # A normal search returns the job's SID right away, so we need to poll for completion
    while True:
        while not job.is_ready():
            if time() > start_time + (time_limit*60):
                break
            else:
                pass

        if time() > start_time + (time_limit*60):
            print("\n\njob stopped - query run more then {} minutes. You can change this limitation ('time_limit')\n".format(time_limit))
            return None

        stats = {"isDone": job["isDone"],
                 "doneProgress": float(job["doneProgress"]) * 100,
                 "scanCount": int(job["scanCount"]),
                 "eventCount": int(job["eventCount"]),
                 "resultCount": int(job["resultCount"])}

        status = ("\rquery status: %(doneProgress)03.1f%%   %(scanCount)d scanned   "
                  "%(eventCount)d matched   %(resultCount)d results") % stats

        sys.stdout.write(status)
        sys.stdout.flush()
        if stats["isDone"] == "1":
            sys.stdout.write("\n\nDone!\n\n")
            break

        sleep(0.01)

    job_results = job.results(output_mode='csv', count=0)

    print('query succeed\n')

    # read results
    results = job_results.read()
    print('read results succeed\n')

    if 'job' in locals():
        job.cancel()
        print("job finished and canceled\n")

    # transform results to DataFrame
    try:
        df = pd.read_csv(BytesIO(results), encoding='utf8', sep=',', low_memory=False)

    except:
        print('finished! number of rows: {}\n'.format(0))
        return None

    # drop Splunk columns which didn't declared in the query
    df.drop(columns=[col for col in df.columns if col[0] == '_'], inplace=True)

    print('finished! number of rows: {}\n'.format(len(df)))

    # missing results warning
    if len(df) == 50000:
        print('''Warning! Splunk API resutls is limited to 50,000 rows. You may have missing rows.
please update your query\n''')

    return df

############################################ loop_over_splunk #################################################

def loop_over_splunk(username, password, host, port, query_kwargs, time_args={}, loop_kwargs=[]):
    '''This function using loop for high volume queries of Splunk database, to overcome the
    Splunk API limitation of 50,000 results per query.
    The function using splunk_query_builder and read_splunk functions.

    Args:
        username (str): Splunk username.
        password (str): Splunk password.
        host (str): Splunk host.
        port (int): Splunk management port.
        query_kwargs (dict): kwargs for splunk_query_builder function. These kwargs will be the default query kwargs
                            for all sub queries.
        time_args (dict): dictionary of time args for the query - start_time, end_time and freq. Time args format
                       most fit pd.date_range function args - start, end and freq. Note that when time_args is used
                       'earliest' and 'latest' kwargs in query_kwargs will be ignored (default: empty dict).
        loop_kwargs (list): list of query_kwargs dicts for sub queries. Note that query kwargs in loop_kwargs arg can
                            replace the default settings of query_kwargs arg, or set new kwargs for the sub query
                            (default: empty list).

    Returns:
        DataFrame: query results.
    '''

    if not time_args and not loop_kwargs:
        print ('No loops have requested\n\n')

    if time_args:
        earliest_latest = get_dates_range(time_args['start_time'],
                                                        time_args['end_time'],
                                                        time_args['freq'])
    else:
        earliest_latest = [(False,False)] #empty value for loop to iterate

    if not loop_kwargs:
        loop_kwargs.append({}) #empty value for loop to iterate

    base_query_kwargs = dict(query_kwargs)

    df = pd.DataFrame()

    # start loop
    for e in loop_kwargs:
        for col in e:
            query_kwargs[col] = e[col]

        for earliest, latest in earliest_latest:
            if earliest and latest:
                query_kwargs['earliest'] = earliest
                query_kwargs['latest'] = latest

            subdf = read_splunk(splunk_query_builder(**query_kwargs),
                            host=host, port=port, username=username, password=password, time_limit=2)

            if isinstance(subdf, pd.DataFrame) and len(subdf) == 50000: #50,000 results is Splunk API limitation
                raise ValueError('')
                break

            else:
                df = df.append(subdf)

            query_kwargs = restart_cols_settings(['earliest','latest'], query_kwargs, base_query_kwargs)

        query_kwargs = restart_cols_settings(list(e.keys()), query_kwargs, base_query_kwargs)

    df.drop_duplicates(inplace=True)

    return df


def get_dates_range(start, end, freq):
    dates = pd.date_range(start=start, end=end, freq=freq).tolist()

    if end not in dates:
        dates.append(pd.to_datetime(end))

    dates = [date.strftime("%m/%d/%Y:%H:%M:%S") for date in dates]

    dates_range = \
        [('"{}"'.format(date),
          '"{}"'.format(dates[dates.index(date) + 1])) for date in dates if dates.index(date) < len(dates) - 1]

    return dates_range


def restart_cols_settings(cols_list, query_kwargs, base_query_kwargs):
    for col in cols_list:
        if col in base_query_kwargs:
            query_kwargs[col] = base_query_kwargs[col]
        else:
            query_kwargs.pop(col, None)

    return query_kwargs