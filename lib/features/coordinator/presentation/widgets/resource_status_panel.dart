import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';

class ResourceStatusPanel extends StatelessWidget {
  const ResourceStatusPanel({super.key});

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Resource status', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
          const SizedBox(height: 8),
          Text(
            // TODO(Phase1): aggregate hospitals/shelters/volunteers repositories.
            'Shows availability across hospitals, shelters, and volunteer pools.',
            style: AppTextStyles.bodyMuted(),
          ),
        ],
      ),
    );
  }
}
