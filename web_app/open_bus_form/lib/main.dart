import 'package:flutter/material.dart';
import 'option_drop_down_widget.dart';
import 'package:fluttertoast/fluttertoast.dart';
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


  bool validateUserInput() {
    return (_chosenBusLine != null &&
            _chosenBusStop != null &&
            _chosenBusDirection != null);
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
                    if (validateUserInput()) {
                      _date = new DateTime.now();
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
