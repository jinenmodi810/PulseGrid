import 'package:flutter/material.dart';

import '../../app/theme/app_colors.dart';
import '../../app/theme/app_text_styles.dart';

enum StatusBadgeTone { neutral, success, warning, danger }

class StatusBadge extends StatelessWidget {
  const StatusBadge({super.key, required this.label, this.tone = StatusBadgeTone.neutral});

  final String label;
  final StatusBadgeTone tone;

  Color _background() {
    return switch (tone) {
      StatusBadgeTone.neutral => AppColors.border.withValues(alpha: 0.35),
      StatusBadgeTone.success => AppColors.success.withValues(alpha: 0.12),
      StatusBadgeTone.warning => AppColors.warning.withValues(alpha: 0.12),
      StatusBadgeTone.danger => AppColors.danger.withValues(alpha: 0.12),
    };
  }

  Color _foreground() {
    return switch (tone) {
      StatusBadgeTone.neutral => AppColors.textSecondary,
      StatusBadgeTone.success => AppColors.success,
      StatusBadgeTone.warning => AppColors.warning,
      StatusBadgeTone.danger => AppColors.danger,
    };
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: _background(),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: AppTextStyles.label().copyWith(color: _foreground()),
      ),
    );
  }
}
