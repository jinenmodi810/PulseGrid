import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';

class CreditsCard extends StatelessWidget {
  const CreditsCard({
    super.key,
    required this.credits,
    this.subtitle = 'Earned through completed field tasks.',
  });

  final int credits;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Row(
        children: [
          const Icon(Icons.stars),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Volunteer credits', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: AppTextStyles.bodyMuted(),
                ),
              ],
            ),
          ),
          Text('$credits', style: AppTextStyles.titleLarge().copyWith(fontSize: 28)),
        ],
      ),
    );
  }
}
