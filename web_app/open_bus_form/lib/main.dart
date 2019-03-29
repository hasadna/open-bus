import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:collection';

import 'option_drop_down_widget.dart';
import 'login_page.dart';


void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Open Bus User Form',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      //home: MyHomePage(title: 'Open Bus User Form'),
      home: LoginPage(),
      routes: {
        "/main": (_) => new MyHomePage(
          title: 'Open Bus User Form'
        ),
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
  String _chosenBusStop = null;
  String _chosenBusDirection = null;
  DateTime _date = null;

  Map<String, String> _dataToSend = new HashMap<String, String>();


  bool _validateUserInput() {
    return (_chosenBusLine != null &&
            _chosenBusStop != null &&
            _chosenBusDirection != null);
  }

   Future<String> _getValueFromSharedPrefs(String key) async {
      SharedPreferences prefs = await SharedPreferences.getInstance();
      return prefs.getString(key) ?? '';
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
                valueReturned: (busLine) {
                  _chosenBusLine = busLine;
                },
              ),
              new OptionDropDownWidget(
                defaultOptionText: "Please Choose The Stop You Are At",
                defaultTitleText: "Bus Stop",
                urlToFetchData: "",
                valueReturned: (busStop) {
                  _chosenBusStop = busStop;
                },
              ),
              new OptionDropDownWidget(
                defaultOptionText: "Please Choose A Direction",
                defaultTitleText: "Bus Direction",
                urlToFetchData: "",
                valueReturned: (busDirection) {
                  _chosenBusDirection = busDirection;
                },
              ),
             new RaisedButton(
                 onPressed: () {
                    if (_validateUserInput()) {
                      _date = new DateTime.now();
                      Future<String> username = _getValueFromSharedPrefs("Username");
                      username.then((user) {
                        _dataToSend["Username"] = user;
                      });
                      Future<String> usermail = _getValueFromSharedPrefs("UserEmail");
                      usermail.then((mail) {
                        _dataToSend["UserMail"] = mail;
                      });
                      //TODO send data to backend

                    } else {
                      Fluttertoast.showToast(
                          msg: "You have failed to provide the necessary input",
                          toastLength: Toast.LENGTH_LONG,
                          timeInSecForIos: 1,
                          backgroundColor: Colors.red,
                          textColor: Colors.white,
                          fontSize: 16.0
                      );
                    }
                 },
               child: Text("Submit"),
             )
          ],
        ),
      ),
    );
  }
}
