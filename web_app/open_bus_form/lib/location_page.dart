import 'package:flutter/material.dart';
import 'package:simple_permissions/simple_permissions.dart';
import 'package:location/location.dart';



class LocationPage extends StatefulWidget {

  @override
  _LocationPageState createState() => _LocationPageState();

}


class _LocationPageState extends State<LocationPage> {

  Map<String, double> userLocation = {};

  Future<Map<String, double>> gatherUserLocation() async{
    Location location = new Location();
    String error = null;
    try {
      userLocation = await location.getLocation();
    } catch (e) {
      print("Error when getting location " + e.toString());
      userLocation = null;
    }
    return userLocation;
  }


  void requestLocationPermission(BuildContext context) async {
    bool locationPermissionStatus = await SimplePermissions.checkPermission(Permission.AccessFineLocation);
    print("Location Permission status is " + locationPermissionStatus.toString());
    if (!locationPermissionStatus) {
      PermissionStatus requestPermissionStatus = await SimplePermissions.requestPermission(Permission.AccessFineLocation);
      switch (requestPermissionStatus) {
        case PermissionStatus.authorized : {
            Navigator.pushReplacementNamed(context, "/bus_stop");

//          Future<Map<String, double>> currentLocation = gatherUserLocation();
//          currentLocation.then((loc) {
//            if (loc != null) {
//              print ("Longitude " + loc["longitude"].toString());
//              print ("Latitude " + loc["latitude"].toString());
//            } else {
//              print ("Location is null");
//              Navigator.pushReplacementNamed(context, "/bus_stop");
//            }
//          });
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

      //Location permission already granted
    } else {
      Future<Map<String, double>> currentLocation = gatherUserLocation();
      currentLocation.then((loc) {
        if (loc != null) {
          print ("Longitude " + loc["longitude"].toString());
          print ("Latitude " + loc["latitude"].toString());
        } else {
          print ("Location is null");
          Navigator.pushReplacementNamed(context, "/bus_stop");
        }
      });
    }
  }

  @override
  void initState() {
    super.initState();
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
        ),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 16.0),
          child: RaisedButton(
            onPressed: () {
                requestLocationPermission(context);
            },
            child: Text('Get Location Permission'),
            color: Colors.green
          ),
        ),
        ]
      ),
    );
  }

}