import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/providers.dart';
import '../../../../core/services/realtime_service.dart';
import '../../../auth/presentation/providers/auth_providers.dart';
import 'volunteer_task_providers.dart';

Future<void> _closeChannel(WebSocketChannel? ch) async {
  try {
    await ch?.sink.close();
  } catch (_) {}
}

void _invalidateVolunteerSideEffects(Ref ref) {
  ref.invalidate(volunteerTasksForSessionProvider);
  ref.invalidate(volunteerProfileBySessionProvider);
  ref.invalidate(dashboardSummaryProvider);
  ref.invalidate(rewardsProvider);
}

/// One socket per [volunteerId].
final volunteerRealtimeProvider = StreamProvider.autoDispose.family<int, String>((ref, volunteerId) async* {
  if (volunteerId.isEmpty) return;
  final wsBase = ref.watch(wsBaseUrlProvider);
  final uri = Uri.parse('$wsBase/ws/volunteers/${Uri.encodeComponent(volunteerId)}');
  WebSocketChannel? channel;
  try {
    channel = WebSocketChannel.connect(uri);
  } catch (_) {
    return;
  }
  ref.onDispose(() {
    unawaited(_closeChannel(channel));
  });
  try {
    await for (final raw in channel.stream) {
      final data = decodeRealtimeMessage(raw);
      final event = data?['event'] as String?;
      if (isVolunteerRefreshEvent(event)) {
        _invalidateVolunteerSideEffects(ref);
      }
      yield 1;
    }
  } catch (_) {}
});

/// Uses session volunteer id so tasks / rewards / profile share one subscription when active.
final volunteerRealtimeBySessionProvider = StreamProvider.autoDispose<int>((ref) async* {
  final storage = ref.watch(storageServiceProvider);
  final id = await storage.getString(SessionKeys.graphVolunteerId);
  if (id == null || id.isEmpty) {
    yield 0;
    return;
  }
  final wsBase = ref.watch(wsBaseUrlProvider);
  final uri = Uri.parse('$wsBase/ws/volunteers/${Uri.encodeComponent(id)}');
  WebSocketChannel? channel;
  try {
    channel = WebSocketChannel.connect(uri);
  } catch (_) {
    return;
  }
  ref.onDispose(() {
    unawaited(_closeChannel(channel));
  });
  try {
    await for (final raw in channel.stream) {
      final data = decodeRealtimeMessage(raw);
      final event = data?['event'] as String?;
      if (isVolunteerRefreshEvent(event)) {
        _invalidateVolunteerSideEffects(ref);
      }
      yield 1;
    }
  } catch (_) {}
});
