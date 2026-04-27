import 'dart:io';

import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../../app/constants/api_constants.dart';

/// ===============================================
/// MODE: iOS SIMULATOR / LOCAL DEVELOPMENT
/// -----------------------------------------------
/// - iOS Simulator can access Mac via 127.0.0.1
/// - Android emulator uses 10.0.2.2
/// - Backend expected on port 8002
/// ===============================================
String resolveApiBaseUrl() {
  // iOS Simulator should always hit localhost on the same Mac host.
  // This avoids stale LAN-IP overrides from .env causing timeouts.
  final isIosSimulator =
      Platform.isIOS && Platform.environment.containsKey('SIMULATOR_DEVICE_NAME');
  if (isIosSimulator) {
    return 'http://127.0.0.1:8002';
  }

  // If .env is set, it overrides defaults for physical devices / custom setups.
  final fromEnv = dotenv.maybeGet(ApiConstants.envApiBaseUrl)?.trim();
  if (fromEnv != null && fromEnv.isNotEmpty) {
    return fromEnv.replaceAll(RegExp(r'/+$'), '');
  }

  // 2. Android Emulator
  if (Platform.isAndroid) {
    return 'http://10.0.2.2:8002';
  }

  // 3. iOS Simulator (runs on Mac)
  if (Platform.isIOS) {
    return 'http://127.0.0.1:8002';
  }

  // 4. Default fallback
  return 'http://127.0.0.1:8002';
}