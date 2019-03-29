import 'package:flutter/material.dart';

class Constants extends InheritedWidget {
  static Constants of(BuildContext context) => context.inheritFromWidgetOfExactType(Constants);

  const Constants({Widget child, Key key}): super(key: key, child: child);

  final String usernameKey = 'Username';
  final String usermailKey = 'UserEmail';

  @override
  bool updateShouldNotify(InheritedWidget oldWidget) {
    return false;
  }

}