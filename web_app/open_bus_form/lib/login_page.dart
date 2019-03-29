import 'package:flutter/material.dart';
import 'main.dart';


class LoginPage extends StatefulWidget {

  @override
  _LoginPageState createState() => _LoginPageState();

}


class _LoginPageState extends State<LoginPage> {

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Login To Open Bus Form'),
      ),
      body: LoginForm(),
    );
  }
}

class LoginForm extends StatefulWidget {

  @override
  LoginFormState createState() {
    return LoginFormState();
  }
}

class LoginFormState extends State<LoginForm> {

  final _formKey = GlobalKey<FormState>();

  bool isValidEmail(String email) {
    RegExp regExp = new RegExp(
      r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
      caseSensitive: false,
      multiLine: false,
    );

    return regExp.hasMatch(email);
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          new ListTile(
            leading: const Icon(Icons.person),
            title: TextFormField(
              validator: (value) {
                if (value.isEmpty) {
                  return 'Please enter a username';
                }
              },
              decoration: new InputDecoration(
                  hintText: "Username",
                ),
              ),
            ),
          new ListTile(
            leading: const Icon(Icons.email),
            title: TextFormField(
              validator: (value) {
                if (value.isEmpty || !isValidEmail(value)) {
                  return 'Please enter a valid email';
                }
              },
              decoration: new InputDecoration(
                hintText: "Email",
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 16.0),
            child: RaisedButton(
              onPressed: () {
                if (_formKey.currentState.validate()) {
                  Navigator.pushReplacementNamed(context, "/main");
                }
              },
              child: Text('Submit'),
            ),
          ),
        ],
      ),
    );
  }
}