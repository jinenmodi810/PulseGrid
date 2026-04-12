import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_button.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../incident_tracking/presentation/response_tier_copy.dart';
import '../../data/volunteer_task_item_dto.dart';
import 'task_status_chip.dart';

class TaskCard extends StatelessWidget {
  const TaskCard({
    super.key,
    required this.task,
    required this.onOpenDetail,
    this.onAccept,
  });

  final VolunteerTaskItemDto task;
  final VoidCallback onOpenDetail;
  final VoidCallback? onAccept;

  bool get _canAccept {
    final s = task.status.toLowerCase();
    return s != 'accepted' && s != 'resolved';
  }

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          InkWell(
            onTap: onOpenDetail,
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.place_outlined, size: 22),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          task.incidentType.isEmpty ? 'Incident' : task.incidentType,
                          style: AppTextStyles.titleMedium().copyWith(fontSize: 16),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'ID ${task.incidentId}',
                          style: AppTextStyles.bodyMuted(),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Zone ${task.zoneId} · ${task.priorityLabel}',
                          style: AppTextStyles.bodyMuted(),
                        ),
                        if (task.summaryLine.isNotEmpty) ...[
                          const SizedBox(height: 6),
                          Text(task.summaryLine, style: AppTextStyles.body()),
                        ],
                        if (task.taskSource == 'nearby_open') ...[
                          const SizedBox(height: 4),
                          Text('Open in your zone', style: AppTextStyles.microcopy()),
                        ],
                        if (task.responseTier.isNotEmpty) ...[
                          const SizedBox(height: 4),
                          Text(
                            'Coordination: ${responseTierHeadline(task.responseTier)}',
                            style: AppTextStyles.microcopy(),
                          ),
                        ],
                      ],
                    ),
                  ),
                  TaskStatusChip(status: task.status),
                ],
              ),
            ),
          ),
          if (_canAccept && onAccept != null) ...[
            const SizedBox(height: 12),
            AppButton(
              label: 'Accept task',
              onPressed: onAccept,
              variant: AppButtonVariant.outlined,
            ),
          ],
        ],
      ),
    );
  }
}
