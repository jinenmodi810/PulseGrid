import 'package:flutter/material.dart';

import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';
import '../../domain/local_priority_preview.dart';

class PriorityPreviewCard extends StatelessWidget {
  const PriorityPreviewCard({super.key, required this.preview});

  final LocalPriorityPreview preview;

  Color _accent() {
    return switch (preview.label) {
      'CRITICAL' => AppColors.danger,
      'HIGH' => AppColors.warning,
      'MEDIUM' => AppColors.textSecondary,
      _ => AppColors.success,
    };
  }

  @override
  Widget build(BuildContext context) {
    final accent = _accent();
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Priority preview', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
          const SizedBox(height: 8),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                preview.label,
                style: AppTextStyles.titleMedium().copyWith(
                  fontSize: 22,
                  color: accent,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(width: 12),
              Text(
                preview.score.toStringAsFixed(2),
                style: AppTextStyles.bodyMuted(),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            'Updates as you adjust severity, headcount, and needs — same rules as the server.',
            style: AppTextStyles.bodyMuted(),
            maxLines: 4,
            overflow: TextOverflow.fade,
            softWrap: true,
          ),
        ],
      ),
    );
  }
}
