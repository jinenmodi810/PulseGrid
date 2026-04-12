import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/enums/reward_badge_type.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/status_badge.dart';

class BadgeCard extends StatelessWidget {
  const BadgeCard({super.key, required this.title, required this.badgeType});

  final String title;
  final RewardBadgeType badgeType;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Row(
        children: [
          const Icon(Icons.military_tech),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
                const SizedBox(height: 4),
                Text('Badge tier', style: AppTextStyles.bodyMuted()),
              ],
            ),
          ),
          StatusBadge(label: badgeType.name, tone: StatusBadgeTone.success),
        ],
      ),
    );
  }
}
