import 'package:flutter/material.dart';

import '../../../../core/widgets/status_badge.dart';

/// Compact status for volunteer task rows.
class TaskStatusChip extends StatelessWidget {
  const TaskStatusChip({super.key, required this.status});

  final String status;

  StatusBadgeTone _tone() {
    final s = status.toLowerCase();
    if (s == 'resolved' || s == 'closed') return StatusBadgeTone.success;
    if (s == 'accepted' || s == 'assigned') return StatusBadgeTone.neutral;
    if (s == 'escalated') return StatusBadgeTone.danger;
    if (s == 'open') return StatusBadgeTone.warning;
    return StatusBadgeTone.neutral;
  }

  @override
  Widget build(BuildContext context) {
    return StatusBadge(label: status, tone: _tone());
  }
}
