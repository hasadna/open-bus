import 'package:flutter/material.dart';
import 'option_drop_down_widget.dart';


void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Open Bus User Form',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(title: 'Open Bus User Form'),
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
  DateTime _date = new DateTime.now();


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
                valueReturned: (busLine) {
                  _chosenBusLine = busLine;
                },
              ),
              new OptionDropDownWidget(
                defaultOptionText: "Please Choose The Stop You Are At",
                defaultTitleText: "Bus Stop",
                valueReturned: (busStop) {
                  _chosenBusStop = busStop;
                },
              ),
              new OptionDropDownWidget(
                defaultOptionText: "Please Choose A Direction",
                defaultTitleText: "Bus Direction",
                valueReturned: (busDirection) {
                  _chosenBusDirection = busDirection;
                },
              ),
             new RaisedButton(
                 onPressed: () {
                   print(_chosenBusLine);
                   print(_date);
                 },
               child: Text("Submit"),
             )
          ],
        ),
      ),
    );
  }
}
