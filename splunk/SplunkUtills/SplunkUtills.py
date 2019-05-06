
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
            if isinstance(query_kwargs[param], tuple):
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



def read_splunk(query, username, password, host, port):
    '''This function queries Splunk database.
    Note that function dependencies includes installing splunklib.

    Args:
        query (str): SPL query.
        username (str): Splunk username.
        password (str): Splunk password.
        host (str): Splunk host.
        port (int): Splunk port.

    Returns:
        DataFrame: query results.
    '''

    print('start..\n')

    print('your query:\n {}\n'.format("|\n".join(query.split("|"))))

    # imports
    import sys
    import re
    import pandas as pd
    from io import BytesIO
    from time import sleep

    if 'splunk-sdk-python-1.6.6' not in sys.path:
        try:
            sys.path.append('splunk-sdk-python-1.6.6')
        except:
            None

    import splunklib.client as client

    print('imports completed\n')

    # connect to splunk
    service = client.connect(host=host, port=port, username=username, password=password)
    print('connection succeed\n')

    # query splunk
    kwargs_normalsearch = {"exec_mode": "normal", "count": 0}
    job = service.jobs.create(query, **kwargs_normalsearch)

    # A normal search returns the job's SID right away, so we need to poll for completion
    while True:
        while not job.is_ready():
            pass
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
        print("job_canceled\n")

    # transform results to DataFrame
    try:
        df = pd.read_csv(BytesIO(results), encoding='utf8', sep=',', low_memory=False)

    except:
        print('finished! number of rows: {}\n'.format(0))
        return None

    # drop Splunk columns which didn't decalred in ther query
    df.drop(columns=[col for col in df.columns if col[0] == '_'], inplace=True)

    print('finished! number of rows: {}\n'.format(len(df)))

    # missing results warning
    if len(df) == 50000:
        print('''Warning! Splunk API resutls is limited to 50,000 rows. You may have missing rows.
please update your query\n''')

    return df