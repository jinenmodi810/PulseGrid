import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../../core/services/realtime_service.dart';
import 'organization_providers.dart';

Future<void> _closeChannel(WebSocketChannel? ch) async {
  try {
    await ch?.sink.close();
  } catch (_) {}
}

void _invalidateOrganizationSideEffects(Ref ref) {
  ref.invalidate(organizationIncidentsProvider);
  ref.invalidate(organizationOverviewProvider);
}

/// One socket per organization id (assigned incidents feed).
final organizationRealtimeProvider = StreamProvider.autoDispose.family<int, String>((ref, organizationId) async* {
  if (organizationId.isEmpty) return;
  final wsBase = ref.watch(wsBaseUrlProvider);
  final uri = Uri.parse('$wsBase/ws/organizations/${Uri.encodeComponent(organizationId)}');
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
      if (isOrganizationRefreshEvent(event)) {
        _invalidateOrganizationSideEffects(ref);
      }
      yield 1;
    }
  } catch (_) {}
});

/// Uses session organization id from storage-backed repository.
final organizationRealtimeBySessionProvider = StreamProvider.autoDispose<int>((ref) async* {
  final oid = await ref.watch(organizationSessionIdProvider.future);
  if (oid.isEmpty) {
    yield 0;
    return;
  }
  final wsBase = ref.watch(wsBaseUrlProvider);
  final uri = Uri.parse('$wsBase/ws/organizations/${Uri.encodeComponent(oid)}');
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
      if (isOrganizationRefreshEvent(event)) {
        _invalidateOrganizationSideEffects(ref);
      }
      yield 1;
    }
  } catch (_) {}
});
