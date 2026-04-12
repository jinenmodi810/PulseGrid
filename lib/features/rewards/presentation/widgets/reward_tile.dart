import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';

class RewardTile extends StatelessWidget {
  const RewardTile({super.key, required this.title, required this.description});

  final String title;
  final String description;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
          const SizedBox(height: 6),
          Text(description, style: AppTextStyles.bodyMuted()),
        ],
      ),
    );
  }
}
