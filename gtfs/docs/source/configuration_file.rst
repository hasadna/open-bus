Configuration file
========================

Config Example
**************
| An example for a minimal working config

.. code-block:: python

    {
      "files": {
        "base_directory": "",  # Fill with a full path to the download dir
        "child_directories": {
          "gtfs_feeds": "gtfs_feeds",
          "output": "output",
          "filtered_feeds": "filtered_feeds",
          "logs": "logs"
        }
      },

      "s3": {
        "access_key_id": "Your Access key id",  # Fill with your key parameters
        "secret_access_key": "Your secret access key",  # Fill with your key parameters
        "s3_endpoint_url": "https://ams3.digitaloceanspaces.com",
        "bucket_name": "obus-do2",
      },

      "date_range": ["2019-03-07"],
    }

Parameters description
**********************

.. jsonschema:: ../../gtfs_utils/gtfs_utils/config.schema.json#/schema
.. jsonschema:: ../../gtfs_utils/gtfs_utils/config.schema.json#/definitions/files
.. jsonschema:: ../../gtfs_utils/gtfs_utils/config.schema.json#/definitions/s3

