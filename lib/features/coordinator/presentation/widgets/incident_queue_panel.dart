import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/status_badge.dart';

class IncidentQueuePanel extends StatelessWidget {
  const IncidentQueuePanel({super.key});

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Incident queue', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
          const SizedBox(height: 8),
          Text(
            // TODO(Phase1): bind to coordinator feed / websocket.
            'Drag-and-drop triage will live here.',
            style: AppTextStyles.bodyMuted(),
          ),
          const SizedBox(height: 10),
          const StatusBadge(label: '3 open', tone: StatusBadgeTone.warning),
        ],
      ),
    );
  }
}
