"""
Source: https://github.com/daphshez/gsheet_tools
See there for instructions to creating an api key
"""

import os
from collections import namedtuple

import collections
from apiclient import discovery
from httplib2 import Http
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from itertools import zip_longest
import csv

CLIENT_SECRET = os.path.join(os.path.dirname(__file__), 'client_secret.json')
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

Flags = namedtuple('Flags', 'auth_host_name noauth_local_webserver auth_host_port logging_level')
default_flags = Flags('localhost', 'store_true', [8080, 8090], 'DEBUG')


def get_credentials(client_secret_path=CLIENT_SECRET):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'csv-to-gsheet.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secret_path, SCOPES)
        credentials = tools.run_flow(flow, store, flags=default_flags)
    return credentials


def make_freeze_row_request(sheet_id):
    return {"updateSheetProperties": {"properties":
        {
            "sheetId": sheet_id,
            "gridProperties": {
                "frozenRowCount": 1
            }
        },
        "fields": "gridProperties.frozenRowCount"}}


def make_first_row_bold_request(sheet_id):
    return {"repeatCell": {
        "range": {
            "sheetId": sheet_id,
            "startRowIndex": 0,
            "endRowIndex": 1
        },
        "cell": {
            "userEnteredFormat": {
                "horizontalAlignment": "CENTER",
                "textFormat": {
                    "bold": True
                }
            }
        },
        "fields": "userEnteredFormat(textFormat,horizontalAlignment)"
    }}


def from_gsheet(spreadsheet_id):
    """Returns data the from all the sheets in the spreadsheet, as a list of raws

    :param spreadsheet_id: appears in the urls between '/d/' and '/edit'
    :return: List of tuples, with the sheet name and the sheet rows
    """
    sheets = discovery.build('sheets', 'v4', http=get_credentials().authorize(Http()))
    # get the sheet ids & titles
    sheet_res = sheets.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=False).execute()
    sheet_names = [sheet['properties']['title'] for sheet in sheet_res['sheets']]
    # get the first row from every sheet & determine real number of columns
    res = sheets.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id, ranges=sheet_names).execute()
    return [(vr['range'].split('!')[0].strip("'"), vr['values']) for vr in res['valueRanges']]


def dicts_from_gsheet(spreadsheet_id):
    names_and_rows = from_gsheet(spreadsheet_id)
    names_headers_rows = ((name, rows[0], rows[1:]) for (name, rows) in names_and_rows if len(rows) > 0)
    names_dicts = ((name, [dict(zip_longest(header, row, fillvalue='')) for row in rows])
                   for (name, header, rows) in names_headers_rows)
    return collections.OrderedDict(names_dicts)


def to_gsheet(spreadsheet_name, data, client_secret_path=CLIENT_SECRET):
    """Create a new Google spreadsheet and write all the data into it

    :param spreadsheet_name: the name to give to the spreadsheet
    :param data: dictionary from sheet name, to a list of sequences, each sequence will be written to one raw
    :param client_secret_path:
    :return: the id of the spreadsheet created
    """

    credentials = get_credentials(client_secret_path)
    sheets = discovery.build('sheets', 'v4', http=credentials.authorize(Http()))

    # create spreadsheet
    res = sheets.spreadsheets().create(body={'properties': {'title': spreadsheet_name}}).execute()
    spreadsheet_id = res['spreadsheetId']
    sheet1_id = res['sheets'][0]['properties']['sheetId']

    # create all the sheets needed. delete default sheet1
    requests = [{'addSheet': {'properties': {'title': title}}} for title in list(data.keys())]
    requests += [{'deleteSheet': {'sheetId': sheet1_id}}]
    res = sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': requests}).execute()
    sheet_ids = [reply['addSheet']['properties']['sheetId'] for reply in res['replies']
                 if 'addSheet' in reply]
    # freeze first row for all sheets + apply bold formatting
    requests = [make_freeze_row_request(sheet_id) for sheet_id in sheet_ids]
    requests += [make_first_row_bold_request(sheet_id) for sheet_id in sheet_ids]
    sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': requests}).execute()

    # load data into sheets
    for sheet_name, records in data.items():
        sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                              range=sheet_name,
                                              body={'values': records},
                                              valueInputOption='RAW').execute()

    return spreadsheet_id


def add_sheet(spreadsheet_id, sheet_name, records):
    credentials = get_credentials()
    sheets = discovery.build('sheets', 'v4', http=credentials.authorize(Http()))
    # create all the sheets needed. delete default sheet1
    requests = [{'addSheet': {'properties': {'title': sheet_name, 'index': 0}}}]
    res = sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': requests}).execute()
    sheet_id = [reply['addSheet']['properties']['sheetId'] for reply in res['replies']][0]
    # freeze first row for all sheets + apply bold formatting
    requests = [make_freeze_row_request(sheet_id), make_first_row_bold_request(sheet_id)]
    sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': requests}).execute()
    sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                          range=sheet_name,
                                          body={'values': records},
                                          valueInputOption='RAW').execute()


def csvs_to_gsheet(spreadsheet_name, file_names, sheet_names=None, encoding='utf-8', client_secret_path=CLIENT_SECRET):
    """Write all input files as separate sheets (plies) in one Google Spread Sheet.

    :param spreadsheet_name: how shall we call the spreadsheet?
    :param file_names: the paths of the files to read
    :param sheet_names: names of the sheets, in the same order of the name of the files. If None, name of files will be used.
    :param encoding: encoding of the input files
    :param client_secret_path:
    :return: spreadsheet id of the new spreadsheet
    """

    def get_sheet_name(fn):
        return os.path.split(os.path.splitext(fn)[0])[-1]

    if sheet_names is None:
        sheet_names = [get_sheet_name(file_name) for file_name in file_names]

    assert len(set(sheet_names)) == len(sheet_names), "Repeating values in sheet names %s" % sheet_names

    data = {}
    for file_name in file_names:
        print("Importing %s" % file_name)
        with open(file_name, 'r', encoding=encoding) as f:
            data[get_sheet_name(file_name)] = [tuple(r) for r in csv.reader(f)]
    return to_gsheet(spreadsheet_name, data, client_secret_path)


def gsheet_to_csvs(spreadsheet_id, output_folder):
    for range_name, range_data in from_gsheet(spreadsheet_id):
        with open(os.path.join(output_folder, range_name + '.csv'), 'w', encoding='utf8') as f:
            writer = csv.writer(f, lineterminator='\n')
            for r in range_data:
                writer.writerow(r)


def auto_fit_column_width(spreadsheet_id, client_secret_path=CLIENT_SECRET):
    """The width auto-fit isn't"""
    credentials = get_credentials(client_secret_path)
    sheets = discovery.build('sheets', 'v4', http=credentials.authorize(Http()))
    sheet_res = sheets.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=False).execute()
    sheet_ids = [s['properties']['sheetId'] for s in sheet_res['sheets']]
    column_counts = [s['properties']['gridProperties']['columnCount'] for s in sheet_res['sheets']]
    requests = [
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheetId,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": columns
                }
            }
        } for sheetId, columns in zip(sheet_ids, column_counts)
        ]
    sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': requests}).execute()
