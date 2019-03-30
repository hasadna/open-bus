import 'package:flutter/material.dart';
import 'package:simple_permissions/simple_permissions.dart';


class LocationPage extends StatefulWidget {

  @override
  _LocationPageState createState() => _LocationPageState();

}


class _LocationPageState extends State<LocationPage> {

  void gatherAndsendUserLocation() {

  }

  void requestLocationPermission() async {
    bool locationPermissionStatus = await SimplePermissions.checkPermission(Permission.AccessFineLocation);
    print("Location Permission status is " + locationPermissionStatus.toString());
    if (!locationPermissionStatus) {
      PermissionStatus requestPermissionStatus = await SimplePermissions.requestPermission(Permission.AccessFineLocation);
      switch (requestPermissionStatus) {
        case PermissionStatus.authorized : {
          gatherAndsendUserLocation();
          break;
        }
        case PermissionStatus.denied : {
          print("User denied location permission");
          //TODO ask again?
          break;
        }
        case PermissionStatus.notDetermined : {
          print("Permission status " + requestPermissionStatus.toString());
          //TODO figure out what to do with status not determined (ask again?)
          break;
        }
        case PermissionStatus.deniedNeverAsk:
        case PermissionStatus.restricted : {
          //TODO consider closing the application?
          break;
        }
        default : {
          print("Unknown permission status " + requestPermissionStatus.toString());
        }
      }

    }
  }

  @override
  void initState() {
    super.initState();
    requestLocationPermission();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Requesting Location Permission'),
      ),
      body:Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: <Widget>[
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Center(
            child: new Text(
                "Requesting Location Permission...",
                textAlign: TextAlign.center
            ),
          )
        )

        ]
      ),
    );
  }

}