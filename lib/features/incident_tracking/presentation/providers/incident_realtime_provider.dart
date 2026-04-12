import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../../core/services/realtime_service.dart';
import '../../../help_request/presentation/providers/help_request_providers.dart';
import 'ai_guidance_providers.dart';

/// Subscribes to `/ws/incidents/{id}` and refetches incident detail on relevant events.
final incidentRealtimeProvider = StreamProvider.autoDispose.family<int, String>((ref, incidentId) async* {
  if (incidentId.isEmpty) return;
  final wsBase = ref.watch(wsBaseUrlProvider);
  final uri = Uri.parse('$wsBase/ws/incidents/${Uri.encodeComponent(incidentId)}');
  WebSocketChannel? channel;
  try {
    channel = WebSocketChannel.connect(uri);
  } catch (_) {
    return;
  }
  ref.onDispose(() {
    unawaited(channel?.sink.close());
  });
  try {
    await for (final raw in channel.stream) {
      final data = decodeRealtimeMessage(raw);
      final event = data?['event'] as String?;
      if (isIncidentDetailRefreshEvent(event)) {
        ref.invalidate(incidentDetailProvider(incidentId));
        ref.invalidate(affectedUserGuidanceProvider(incidentId));
        ref.invalidate(organizationIncidentSummaryProvider(incidentId));
        ref.invalidate(volunteerGuidanceProvider(incidentId));
      }
      yield 1;
    }
  } catch (_) {}
});
