import 'dart:io';

import 'package:flutter_dotenv/flutter_dotenv.dart';

import '../../app/constants/api_constants.dart';

/// Resolves API base URL: `.env` wins; otherwise platform-appropriate localhost.
String resolveApiBaseUrl() {
  final fromEnv = dotenv.maybeGet(ApiConstants.envApiBaseUrl)?.trim();
  if (fromEnv != null && fromEnv.isNotEmpty) {
    return fromEnv.replaceAll(RegExp(r'/+$'), '');
  }
  if (Platform.isAndroid) {
    return 'http://10.0.2.2:8000';
  }
  return 'http://127.0.0.1:8000';
}
