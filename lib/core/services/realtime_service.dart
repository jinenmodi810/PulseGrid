import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../network/api_env.dart';

/// Server event names (keep aligned with `backend/app/realtime/event_types.py`).
abstract final class RealtimeEventTypes {
  static const incidentCreated = 'incident_created';
  static const incidentOpenInZone = 'incident_open_in_zone';
  static const incidentAssigned = 'incident_assigned';
  static const incidentAccepted = 'incident_accepted';
  static const incidentCompleted = 'incident_completed';
  static const incidentEscalated = 'incident_escalated';
  static const routeBlocked = 'route_blocked';
  static const dashboardUpdated = 'dashboard_updated';
  static const volunteerCreditsUpdated = 'volunteer_credits_updated';
}

/// HTTP(S) API base URL → WebSocket base (ws / wss).
String httpBaseToWsBase(String httpBase) {
  var b = httpBase.trim();
  if (b.endsWith('/')) {
    b = b.substring(0, b.length - 1);
  }
  if (b.startsWith('https://')) {
    return b.replaceFirst('https://', 'wss://');
  }
  if (b.startsWith('http://')) {
    return b.replaceFirst('http://', 'ws://');
  }
  return 'ws://$b';
}

/// Same origin resolution as [ApiClient.configureBaseUrl] (includes Android emulator host).
final wsBaseUrlProvider = Provider<String>((ref) {
  return httpBaseToWsBase(resolveApiBaseUrl());
});

Map<String, dynamic>? decodeRealtimeMessage(dynamic raw) {
  if (raw is! String) return null;
  try {
    final decoded = jsonDecode(raw);
    if (decoded is Map<String, dynamic>) return decoded;
    if (decoded is Map) return Map<String, dynamic>.from(decoded);
  } catch (_) {
    // Non-JSON keepalive or malformed payloads — ignore quietly.
  }
  return null;
}

bool isDashboardRefreshEvent(String? event) {
  if (event == null) return false;
  if (event == RealtimeEventTypes.dashboardUpdated) return true;
  if (event == RealtimeEventTypes.routeBlocked) return true;
  if (event == RealtimeEventTypes.volunteerCreditsUpdated) return true;
  return event.startsWith('incident_');
}

bool isVolunteerRefreshEvent(String? event) {
  if (event == null) return false;
  if (event == RealtimeEventTypes.volunteerCreditsUpdated) return true;
  if (event == RealtimeEventTypes.dashboardUpdated) return true;
  return event.startsWith('incident_');
}

bool isIncidentDetailRefreshEvent(String? event) {
  if (event == null) return false;
  return event.startsWith('incident_') || event == RealtimeEventTypes.routeBlocked;
}

bool isOrganizationRefreshEvent(String? event) {
  if (event == null) return false;
  return event.startsWith('incident_');
}
