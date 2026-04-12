import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';

class TimelineWidget extends StatelessWidget {
  const TimelineWidget({
    super.key,
    required this.incidentId,
    required this.incidentType,
    required this.status,
    this.createdAt,
  });

  final String incidentId;
  final String incidentType;
  final String status;
  final String? createdAt;

  @override
  Widget build(BuildContext context) {
    final steps = ['Created', 'Triaged', 'Assigned / routing', 'Closed'];
    final s = status.toLowerCase();
    int activeIndex = 0;
    if (s == 'open') activeIndex = 1;
    if (s == 'assigned') activeIndex = 2;
    if (s == 'closed') activeIndex = 3;

    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Progress', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
          const SizedBox(height: 6),
          Text('ID $incidentId · $incidentType', style: AppTextStyles.bodyMuted()),
          if (createdAt != null && createdAt!.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text('Reported $createdAt', style: AppTextStyles.bodyMuted()),
            ),
          const SizedBox(height: 12),
          for (var i = 0; i < steps.length; i++) ...[
            Row(
              children: [
                CircleAvatar(
                  radius: 10,
                  backgroundColor: i <= activeIndex ? Theme.of(context).colorScheme.primary : null,
                  child: Text(
                    '${i + 1}',
                    style: TextStyle(
                      fontSize: 10,
                      color: i <= activeIndex ? Theme.of(context).colorScheme.onPrimary : null,
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    steps[i],
                    style: AppTextStyles.body().copyWith(
                      fontWeight: i == activeIndex ? FontWeight.w600 : FontWeight.normal,
                    ),
                  ),
                ),
              ],
            ),
            if (i != steps.length - 1) const Divider(height: 18),
          ],
          const SizedBox(height: 8),
          Text(
            // TODO(Phase1B+): subscribe to incident event stream / websocket for live step updates.
            'Steps update when responders update incident status.',
            style: AppTextStyles.bodyMuted(),
          ),
        ],
      ),
    );
  }
}
