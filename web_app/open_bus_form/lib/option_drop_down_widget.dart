import 'package:flutter/material.dart';

class OptionDropDownWidget extends StatefulWidget {

  final ValueChanged<String> valueReturned;

  OptionDropDownWidget({Key key, this.defaultOptionText : "", this.defaultTitleText: "", this.urlToFetchData: "", this.inputData: null , this.valueReturned})
      : super(key: key);

  final String defaultOptionText;
  final String defaultTitleText;
  final String urlToFetchData;
  final List<String> inputData;

  @override
  _OptionDropDownWidgetState createState() => _OptionDropDownWidgetState();

}


class _OptionDropDownWidgetState extends State<OptionDropDownWidget> {
  List<DropdownMenuItem<String>> _data = [];
  String _chosenBusLine = null;


  void loadData() {
    //TODO add call to fetch data using urlToFetchData
    _data = [];
    for(int i = 0; i < widget.inputData.length; i++) {
      _data.add(new DropdownMenuItem(
        child: new Text(widget.inputData[i]),
        value: widget.inputData[i],
      ));
    }
  }

  @override
  Widget build(BuildContext context) {
    loadData();
    return Column(
      children: <Widget> [
        new Text(
            widget.defaultTitleText
        ),
        DropdownButton(
        value: _chosenBusLine,
        items: _data,
        hint: new Text(widget.defaultOptionText),
        onChanged: (value) {
          _chosenBusLine = value;
          widget.valueReturned(_chosenBusLine);
          setState(() {

          });
        }
       )
      ],
    );
  }
}