import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';

class MetricsPanel extends StatelessWidget {
  const MetricsPanel({super.key});

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Live metrics', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
          const SizedBox(height: 8),
          Text(
            // TODO(Phase1): wire analytics events + time-series charts.
            'Throughput, response times, and SLA adherence.',
            style: AppTextStyles.bodyMuted(),
          ),
        ],
      ),
    );
  }
}
