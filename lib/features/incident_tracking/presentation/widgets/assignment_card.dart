import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/status_badge.dart';

class AssignmentCard extends StatelessWidget {
  const AssignmentCard({
    super.key,
    required this.incidentStatus,
    required this.assignmentHeadline,
    this.subtitle,
  });

  final String incidentStatus;
  final String assignmentHeadline;
  final String? subtitle;

  StatusBadgeTone _toneForStatus(String s) {
    final v = s.toLowerCase();
    if (v == 'assigned' || v == 'closed') return StatusBadgeTone.success;
    if (v == 'open' || v == 'pending') return StatusBadgeTone.warning;
    return StatusBadgeTone.neutral;
  }

  @override
  Widget build(BuildContext context) {
    final tone = _toneForStatus(incidentStatus);
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(child: Text('Assignment', style: AppTextStyles.titleMedium().copyWith(fontSize: 16))),
              StatusBadge(label: incidentStatus, tone: tone),
            ],
          ),
          const SizedBox(height: 8),
          Text(assignmentHeadline, style: AppTextStyles.body()),
          if (subtitle != null && subtitle!.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(subtitle!, style: AppTextStyles.bodyMuted()),
          ],
        ],
      ),
    );
  }
}
