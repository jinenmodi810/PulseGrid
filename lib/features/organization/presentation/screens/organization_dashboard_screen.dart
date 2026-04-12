import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/layout/screen_insets.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../auth/presentation/utils/session_navigation.dart';
import '../../../coordinator/presentation/providers/dashboard_realtime_provider.dart';
import '../../../coordinator/presentation/widgets/dashboard_summary_strip.dart';
import '../providers/organization_providers.dart';
import '../providers/organization_realtime_provider.dart';

class OrganizationDashboardScreen extends ConsumerWidget {
  const OrganizationDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.watch(dashboardRealtimeProvider);
    ref.watch(organizationRealtimeBySessionProvider);
    final overview = ref.watch(organizationOverviewProvider);
    final incidents = ref.watch(organizationIncidentsProvider);

    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Operations overview'),
        automaticallyImplyLeading: false,
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        actions: [
          IconButton(
            icon: const Icon(Icons.person_outline),
            tooltip: 'Organization profile',
            onPressed: () => context.push(AppRoutes.organizationProfile),
          ),
          PopupMenuButton<String>(
            onSelected: (value) async {
              if (value == 'signout') {
                await signOutAndGoLanding(ref, context);
              }
            },
            itemBuilder: (context) => const [
              PopupMenuItem(value: 'signout', child: Text('Sign out')),
            ],
          ),
        ],
      ),
      body: SafeArea(
        top: false,
        child: ListView(
          keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
          padding: ScreenInsets.listVertical(context),
          children: [
          overview.when(
            loading: () => const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator())),
            error: (e, _) => Text(
              e.toString().replaceFirst('Exception: ', ''),
              style: AppTextStyles.body(),
              maxLines: 5,
              overflow: TextOverflow.ellipsis,
            ),
            data: (o) => Container(
              width: double.infinity,
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: AppColors.surfaceCard,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.borderSubtle),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    o.name,
                    style: AppTextStyles.titleMedium().copyWith(fontSize: 20, fontWeight: FontWeight.w600),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 6),
                  Text(
                    '${o.orgType.replaceAll('_', ' ')} · Zone ${o.zoneId}',
                    style: AppTextStyles.bodyMuted(),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    o.active ? 'Status: accepting assignments' : 'Status: paused',
                    style: AppTextStyles.body(),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Active assigned incidents: ${o.assignedIncidentsOpen}',
                    style: AppTextStyles.body().copyWith(fontWeight: FontWeight.w600),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (o.capacity.isNotEmpty) ...[
                    const SizedBox(height: 14),
                    Text(
                      'Coverage and capacity',
                      style: AppTextStyles.titleMedium().copyWith(fontSize: 15),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    ...o.capacity.entries.take(6).map(
                          (e) => Padding(
                            padding: const EdgeInsets.only(bottom: 4),
                            child: Text(
                              '${e.key}: ${e.value}',
                              style: AppTextStyles.microcopy(),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 18),
          const DashboardSummaryStrip(),
          const SizedBox(height: 18),
          Text(
            'Shortcuts',
            style: AppTextStyles.titleMedium().copyWith(fontSize: 16),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 10),
          _NavTile(
            icon: Icons.list_alt_outlined,
            title: 'Incidents',
            subtitle: 'Assigned and routed requests for your team',
            onTap: () => context.push(AppRoutes.organizationIncidents),
          ),
          const SizedBox(height: 10),
          _NavTile(
            icon: Icons.tune_outlined,
            title: 'Resources',
            subtitle: 'Beds, transport, shelter, and readiness',
            onTap: () => context.push(AppRoutes.organizationResources),
          ),
          const SizedBox(height: 10),
          _NavTile(
            icon: Icons.badge_outlined,
            title: 'Profile',
            subtitle: 'Organization identity and contact',
            onTap: () => context.push(AppRoutes.organizationProfile),
          ),
          const SizedBox(height: 22),
          Text(
            'Needs attention',
            style: AppTextStyles.titleMedium().copyWith(fontSize: 16),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 8),
          incidents.when(
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
            data: (list) {
              final esc = list.where((e) => e.escalationRequired).toList();
              if (esc.isEmpty) {
                return Text(
                  'No escalations on your queue right now.',
                  style: AppTextStyles.bodyMuted(),
                  maxLines: 3,
                  overflow: TextOverflow.fade,
                  softWrap: true,
                );
              }
              return Column(
                children: esc
                    .map(
                      (e) => ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: const Icon(Icons.priority_high, color: AppColors.danger),
                        title: Text(
                          e.incidentType,
                          style: AppTextStyles.body().copyWith(fontWeight: FontWeight.w600),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        subtitle: Text(
                          '${e.priorityLabel} · ${e.incidentId}',
                          style: AppTextStyles.microcopy(),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    )
                    .toList(),
              );
            },
          ),
        ],
        ),
      ),
    );
  }
}

class _NavTile extends StatelessWidget {
  const _NavTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: AppColors.surfaceCard,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(icon, color: AppColors.primary),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: AppTextStyles.valueCardTitle(),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    Text(
                      subtitle,
                      style: AppTextStyles.valueCardSubtitle(),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: AppColors.textTertiary),
            ],
          ),
        ),
      ),
    );
  }
}
