import argparse
import collections
import configparser



def _parse_config(config_file_name):
    with open(config_file_name) as f:
            # add section header because config parser requires it
        config_file_content = '[Section]\n' + f.read()
    config = configparser.ConfigParser()
    config.read_string(config_file_content)
    string_keys = ["database_pass", "database_user",
                   "database_name", "database_port","database_host"]
    bool_keys = []
    config_dict = {k: config['Section'][k] for k in string_keys}
    # parse booleans manually
    for key in bool_keys:
        value = config['Section'][key].lower()
        if value != 'true' and value != 'false':
            raise Exception('Configuration error: value for key %s should be True or False' % key)
        config_dict[key] = True if value == 'true' else False
    # the code expects an object and not a dictionary (so you can do args.siri_user, rather than args['siri_user'])
    return collections.namedtuple('Args', string_keys + bool_keys)(**config_dict)

def get_connection_parameters(config_file_name):
    data = _parse_config(config_file_name)
    return {'database':data.database_name,
            'user':data.database_user,
            'password':data.database_pass,
            'host':data.database_host,
            'port':data.database_port}









def get_args_from_cli(input):
    parser = argparse.ArgumentParser("update siri real time table application")
    parser.add_argument('--config_file', '-c', metavar='<PATH>', help='configuration file of db connection')
    parser.add_argument('--date_for_query', '-d', metavar='<DATE>', help='date for query format: 2017-02-27')
    return parser.parse_args(input[1:])

def wrapper(cli_input):
    args = get_args_from_cli(cli_input)
    c = get_connection_parameters(args.config_file)
    d = args.date_for_query
    return dict(connection=c, date=d)




