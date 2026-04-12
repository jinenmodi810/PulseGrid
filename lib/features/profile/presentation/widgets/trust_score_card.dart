import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/status_badge.dart';

class TrustScoreCard extends StatelessWidget {
  const TrustScoreCard({super.key, required this.score});

  final double score;

  @override
  Widget build(BuildContext context) {
    final pct = (score.clamp(0, 1) * 100).round();
    return AppCard(
      child: Row(
        children: [
          const Icon(Icons.verified_user_outlined),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Trust score', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
                const SizedBox(height: 4),
                Text(
                  // TODO: derive from completed tasks and verification events when available.
                  'Reflects reliability from completed tasks and community feedback.',
                  style: AppTextStyles.bodyMuted(),
                ),
              ],
            ),
          ),
          StatusBadge(label: '$pct%', tone: StatusBadgeTone.success),
        ],
      ),
    );
  }
}
