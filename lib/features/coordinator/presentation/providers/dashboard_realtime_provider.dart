import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../../app/providers.dart';
import '../../../../core/services/realtime_service.dart';
import '../../../auth/presentation/providers/auth_providers.dart';

/// Live dashboard counter refresh. Silent on connection errors (REST refresh still works).
final dashboardRealtimeProvider = StreamProvider.autoDispose<int>((ref) async* {
  final wsBase = ref.watch(wsBaseUrlProvider);
  final token = await ref.watch(sessionStoreProvider).getAuthToken();
  if (token == null || token.isEmpty) return;
  final uri = Uri.parse('$wsBase/ws/dashboard').replace(queryParameters: {'token': token});
  WebSocketChannel? channel;
  try {
    channel = WebSocketChannel.connect(uri);
  } catch (_) {
    // TODO(Phase1D+): retry with backoff; surface subtle reconnect UI if needed.
    return;
  }
  ref.onDispose(() {
    unawaited(channel?.sink.close());
  });
  try {
    await for (final raw in channel.stream) {
      final data = decodeRealtimeMessage(raw);
      final event = data?['event'] as String?;
      if (isDashboardRefreshEvent(event)) {
        ref.invalidate(dashboardSummaryProvider);
      }
      yield 1;
    }
  } catch (_) {
    // Dropped connection — user can still pull-to-refresh where available.
  }
});
