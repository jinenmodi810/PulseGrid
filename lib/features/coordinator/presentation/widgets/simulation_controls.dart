import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_button.dart';
import '../../../../core/widgets/app_card.dart';

class SimulationControls extends StatelessWidget {
  const SimulationControls({super.key});

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Simulation', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
          const SizedBox(height: 8),
          Text(
            // TODO(Phase1): drive mock route updates for demos.
            'Fast-forward ETA changes or inject road closures.',
            style: AppTextStyles.bodyMuted(),
          ),
          const SizedBox(height: 12),
          AppButton(label: 'Run sample tick', onPressed: () {}),
        ],
      ),
    );
  }
}
