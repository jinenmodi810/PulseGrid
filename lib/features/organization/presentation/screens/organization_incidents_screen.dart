import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../incident_tracking/presentation/response_tier_copy.dart';
import '../providers/organization_providers.dart';
import '../providers/organization_realtime_provider.dart';

class OrganizationIncidentsScreen extends ConsumerWidget {
  const OrganizationIncidentsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.watch(organizationRealtimeBySessionProvider);
    final async = ref.watch(organizationIncidentsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Assigned incidents'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text(e.toString().replaceFirst('Exception: ', ''))),
        data: (rows) {
          if (rows.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Text('No incidents are assigned to your organization yet.', style: AppTextStyles.body(), textAlign: TextAlign.center),
              ),
            );
          }
          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(organizationIncidentsProvider),
            child: ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: rows.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, i) {
                final e = rows[i];
                return Material(
                  color: AppColors.surfaceCard,
                  borderRadius: BorderRadius.circular(12),
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(child: Text(e.incidentType, style: AppTextStyles.valueCardTitle())),
                            if (e.escalationRequired)
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: AppColors.danger.withValues(alpha: 0.12),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text('Escalation', style: AppTextStyles.microcopy().copyWith(color: AppColors.danger)),
                              ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text('${e.priorityLabel} · ${e.severity} · ${e.status}', style: AppTextStyles.bodyMuted()),
                        if (e.responseTier.isNotEmpty)
                          Text(responseTierHeadline(e.responseTier), style: AppTextStyles.microcopy()),
                        if (e.decisionSummary.isNotEmpty)
                          Padding(
                            padding: const EdgeInsets.only(top: 6),
                            child: Text(
                              e.decisionSummary,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: AppTextStyles.bodyMuted(),
                            ),
                          ),
                        if (e.assignedVolunteerName.isNotEmpty)
                          Padding(
                            padding: const EdgeInsets.only(top: 6),
                            child: Text('Volunteer: ${e.assignedVolunteerName}', style: AppTextStyles.body()),
                          )
                        else if (e.responseTier == 'volunteer_plus_organization')
                          Padding(
                            padding: const EdgeInsets.only(top: 6),
                            child: Text(
                              'Volunteer support is part of the routing plan; assignment may still be pending.',
                              style: AppTextStyles.microcopy(),
                            ),
                          ),
                        Text('Zone ${e.zoneId}', style: AppTextStyles.microcopy()),
                      ],
                    ),
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }
}
