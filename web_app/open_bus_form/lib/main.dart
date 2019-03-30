import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:collection';

import 'option_drop_down_widget.dart';
import 'login_page.dart';
import 'constants.dart';
import 'location_page.dart';
import 'bus_stop_selection_page.dart';
import 'end_page.dart';


void main() => runApp(
   Constants(
    child:  MyApp(),
   ),
);

class MyApp extends StatelessWidget {

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Open Bus User Form',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: LoginPage(),
      routes: {
        "/main": (_) => new MyHomePage(
          title: 'Open Bus User Form'
        ),
        "/location": (_) => new LocationPage(),
        "/bus_stop": (_) => new BusStopSelectionPage(),
        "/end": (_) => new EndPage(),
      }
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _chosenBusLine = null;
  String _reportingReason = null;

  Map<String, String> _dataToSend = new HashMap<String, String>();


  bool _validateUserInput() {
    return (_chosenBusLine != null &&
        _reportingReason != null);
  }

   Future<String> _getValueFromSharedPrefs(String key) async {
      SharedPreferences prefs = await SharedPreferences.getInstance();
      return prefs.getString(key) ?? '';
  }

  void _handleSendingData() {

    Future<String> username = _getValueFromSharedPrefs(Constants.of(context).usernameKey);
    username.then((user) {
      _dataToSend[Constants.of(context).usernameKey] = user;
    });
    Future<String> usermail = _getValueFromSharedPrefs(Constants.of(context).usermailKey);
    usermail.then((mail) {
      _dataToSend[Constants.of(context).usermailKey] = mail;
    });
    _dataToSend[(Constants.of(context).dateKey)] = new DateTime.now().toString();
    
    print("Sending data...");
    //TODO send data to backend
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: <Widget>[
              new OptionDropDownWidget(
                defaultOptionText: "Please Choose A Bus Line",
                defaultTitleText: "Bus Line",
                urlToFetchData: "",
                inputData: ["Line 1", "Line 52", "Line 369"],
                valueReturned: (busLine) {
                  _chosenBusLine = busLine;
                },
              ),
              new OptionDropDownWidget(
                defaultOptionText: "What Happened?",
                defaultTitleText: "Reason for report",
                urlToFetchData: "",
                inputData: ["Bus is late", "Bus never arrived", "Bus full"],
                valueReturned: (reportReason) {
                  _reportingReason = reportReason;
                },
              ),
             new RaisedButton(
                 onPressed: () {
                    if (_validateUserInput()) {
                      _handleSendingData();
                      Navigator.pushReplacementNamed(context, "/end");
                    } else {
                      Fluttertoast.showToast(
                          msg: "Please fill out the form",
                          toastLength: Toast.LENGTH_SHORT,
                          timeInSecForIos: 1,
                          backgroundColor: Colors.red,
                          textColor: Colors.white,
                          fontSize: 16.0
                      );
                    }
                 },
               child: Text("Submit"),
               color: Colors.green
             )
          ],
        ),
      ),
    );
  }
}
