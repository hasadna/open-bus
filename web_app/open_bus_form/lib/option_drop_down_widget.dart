import 'package:flutter/material.dart';

class OptionDropDownWidget extends StatefulWidget {

  OptionDropDownWidget({Key key, this.defaultOptionText : null})
      : super(key: key);

  final String defaultOptionText;

  @override
  _OptionDropDownWidgetState createState() => _OptionDropDownWidgetState();

}


class _OptionDropDownWidgetState extends State<OptionDropDownWidget> {
  List<DropdownMenuItem<String>> _data = [];
  String _chosenBusLine = null;


  void loadData() {
    _data = [];
    _data.add(new DropdownMenuItem(
        child: new Text("Line 1"),
        value: "Line 1",
      ));

    _data.add(new DropdownMenuItem(
      child: new Text("Line 2"),
      value: "Line 2",
    ));

    _data.add(new DropdownMenuItem(
      child: new Text("Line 3"),
      value: "Line 3",
    ));
  }

  @override
  Widget build(BuildContext context) {
    loadData();
    return DropdownButton(
        value: _chosenBusLine,
        items: _data,
        hint: new Text(widget.defaultOptionText),
        onChanged: (value) {
          _chosenBusLine = value;
          setState(() {

          });
        }
    );
  }
}