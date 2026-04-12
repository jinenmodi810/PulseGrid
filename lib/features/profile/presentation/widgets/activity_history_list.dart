import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';

class ActivityHistoryList extends StatelessWidget {
  const ActivityHistoryList({super.key});

  @override
  Widget build(BuildContext context) {
    const items = ['Opened incident draft', 'Viewed support directory', 'Visited rewards'];

    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Recent activity', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
          const SizedBox(height: 8),
          for (final item in items)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  const Icon(Icons.history, size: 18),
                  const SizedBox(width: 8),
                  Expanded(child: Text(item, style: AppTextStyles.body())),
                ],
              ),
            ),
          Text(
            'A full activity log will appear here in a future update.',
            style: AppTextStyles.bodyMuted(),
          ),
        ],
      ),
    );
  }
}
