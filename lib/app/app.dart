import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'constants/app_constants.dart';
import 'router.dart';
import 'theme/app_theme.dart';

class PulseGridApp extends StatefulWidget {
  const PulseGridApp({super.key, required this.initialLocation});

  final String initialLocation;

  @override
  State<PulseGridApp> createState() => _PulseGridAppState();
}

class _PulseGridAppState extends State<PulseGridApp> {
  late final GoRouter _router = buildAppRouter(initialLocation: widget.initialLocation);

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: AppConstants.appName,
      theme: buildAppTheme(),
      routerConfig: _router,
      debugShowCheckedModeBanner: false,
    );
  }
}
