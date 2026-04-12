import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/status_badge.dart';

class RouteStatusCard extends StatelessWidget {
  const RouteStatusCard({
    super.key,
    required this.routeStatus,
    this.etaMinutes,
  });

  final String routeStatus;
  final int? etaMinutes;

  @override
  Widget build(BuildContext context) {
    final etaLine = etaMinutes != null ? 'Volunteer ETA about $etaMinutes min (demo estimate).' : null;
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(child: Text('Route status', style: AppTextStyles.titleMedium().copyWith(fontSize: 16))),
              StatusBadge(label: routeStatus, tone: StatusBadgeTone.neutral),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            etaLine ??
                // TODO(Phase1B+): live map + websocket updates from routing service.
                'Routing is simulated until map and telemetry are connected.',
            style: AppTextStyles.bodyMuted(),
          ),
        ],
      ),
    );
  }
}
