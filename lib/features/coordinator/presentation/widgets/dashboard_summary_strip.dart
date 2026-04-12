import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../auth/data/auth_repository.dart' show DashboardSummary;
import '../../../auth/presentation/providers/auth_providers.dart';

/// Live counts from FastAPI `/dashboard/summary` (Neo4j-backed).
class DashboardSummaryStrip extends ConsumerWidget {
  const DashboardSummaryStrip({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(dashboardSummaryProvider);

    return async.when(
      data: (DashboardSummary s) {
        return Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
          decoration: BoxDecoration(
            color: AppColors.surfaceCard,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppColors.borderSubtle),
          ),
          child: Wrap(
            spacing: 12,
            runSpacing: 10,
            alignment: WrapAlignment.spaceBetween,
            children: [
              _Metric(label: 'Active incidents', value: '${s.activeIncidents}'),
              _Metric(label: 'Volunteers', value: '${s.availableVolunteers}'),
              _Metric(label: 'Hospitals', value: '${s.hospitalsAvailable}'),
              _Metric(label: 'Shelters', value: '${s.sheltersAvailable}'),
              _Metric(label: 'Pending', value: '${s.pendingRequests}'),
              _Metric(label: 'Resolved', value: '${s.resolvedRequests}'),
            ],
          ),
        );
      },
      loading: () => const LinearProgressIndicator(minHeight: 3),
      error: (err, _) => Text(
        'Unable to load live metrics. Check API and Neo4j.',
        style: AppTextStyles.bodyMuted(),
        maxLines: 3,
        overflow: TextOverflow.ellipsis,
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  const _Metric({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 104,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            value,
            style: AppTextStyles.titleMedium().copyWith(fontSize: 20),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          Text(
            label,
            style: AppTextStyles.microcopy(),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
