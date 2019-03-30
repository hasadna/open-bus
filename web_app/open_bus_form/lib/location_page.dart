import 'package:flutter/material.dart';


class LocationPage extends StatefulWidget {

  @override
  _LocationPageState createState() => _LocationPageState();

}


class _LocationPageState extends State<LocationPage> {

  void requestLocationPermission() {

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
        title: Text('Login To Open Bus Form'),
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