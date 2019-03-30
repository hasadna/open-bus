import 'package:flutter/material.dart';
import 'option_drop_down_widget.dart';


class BusStopSelectionPage extends StatefulWidget {

  @override
  _BusStopSelectionPageState createState() => _BusStopSelectionPageState();

}


class _BusStopSelectionPageState extends State<BusStopSelectionPage> {
  @override
  Widget build(BuildContext context) {

    return Scaffold(
      appBar: AppBar(
        title: Text("Select Your Bus Stop"),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: <Widget>[
            new ListTile(
              leading: const Icon(Icons.directions_bus),
              title: OptionDropDownWidget(
                defaultOptionText: "Please Choose Your Bus Station",
                defaultTitleText: "Bus Station",
                inputData: ["Station 1", "Station 2", "Station 3"],
                urlToFetchData: "",
                valueReturned: (busStation) {
                },
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 16.0),
              child: RaisedButton(
                onPressed: () {
                  Navigator.pushReplacementNamed(context, "/main");
                },
                child: Text('Submit'),
                color: Colors.lightBlue
              ),
            ),
          ],
        ),
      ),
    );
  }



}