import 'package:flutter/material.dart';


class EndPage extends StatefulWidget {
  @override
  _EndPageState createState() => _EndPageState();
}


class _EndPageState extends State<EndPage> {
  @override
  Widget build(BuildContext context) {

    return Scaffold(
      appBar: AppBar(
        title: Text("Thanks for your feedback"),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: <Widget>[
            Padding(
                padding: const EdgeInsets.all(16.0),
                child: Center(
                  child: new Text(
                      "Thanks for your feedback",
                      textAlign: TextAlign.center
                  ),
                )
            ),
          ],
        ),
      ),
    );
  }



}