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
import '../../data/organization_dtos.dart';
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
    final analytics = ref.watch(organizationAnalyticsProvider);

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
            'Operational analytics',
            style: AppTextStyles.titleMedium().copyWith(fontSize: 16),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 10),
          analytics.when(
            loading: () => const _AnalyticsLoading(),
            error: (e, _) {
              final msg = e.toString().replaceFirst('Exception: ', '');
              final friendly = msg.toLowerCase().contains('analytics will appear after operational data is processed')
                  ? 'Analytics will appear after operational data is processed.'
                  : msg;
              return _AnalyticsError(message: friendly);
            },
            data: (a) {
              final latestCap = a.capacity.isNotEmpty ? a.capacity.first : null;
              return Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: _KpiCard(
                          title: 'Total incidents',
                          value: '${a.overview.incidentsTotal}',
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: _KpiCard(
                          title: 'Avg assign time',
                          value: _fmtDurationSeconds(a.overview.avgTimeToAssignmentSeconds),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: _KpiCard(
                          title: 'Avg completion',
                          value: _fmtDurationSeconds(a.overview.avgTimeToCompletionSeconds),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: _KpiCard(
                          title: 'Open assigned',
                          value: overview.maybeWhen(
                            data: (o) => '${o.assignedIncidentsOpen}',
                            orElse: () => '-',
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: _KpiCard(
                          title: 'Beds available',
                          value: '${latestCap?.bedsAvailable ?? '-'}',
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: _KpiCard(
                          title: 'Oxygen units',
                          value: '${latestCap?.oxygenUnits ?? '-'}',
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  _SectionCard(
                    title: 'Incidents by zone',
                    child: a.incidentsByZone.isEmpty
                        ? Text(
                            'No zone-level incident analytics yet.',
                            style: AppTextStyles.bodyMuted(),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          )
                        : _IncidentsByZoneChart(items: a.incidentsByZone),
                  ),
                  const SizedBox(height: 10),
                  _SectionCard(
                    title: 'Time to response',
                    child: Column(
                      children: [
                        _kv('Assignment', _fmtDurationSeconds(a.timeToResponse.avgTimeToAssignmentSeconds)),
                        _kv('Acceptance', _fmtDurationSeconds(a.timeToResponse.avgTimeToAcceptanceSeconds)),
                        _kv('Completion', _fmtDurationSeconds(a.timeToResponse.avgTimeToCompletionSeconds)),
                      ],
                    ),
                  ),
                  const SizedBox(height: 10),
                  _SectionCard(
                    title: 'Organization capacity analytics',
                    child: latestCap == null
                        ? Text(
                            'No capacity analytics yet.',
                            style: AppTextStyles.bodyMuted(),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          )
                        : Column(
                            children: [
                              _kv('Captured', latestCap.capturedAt ?? '-'),
                              _kv('Beds', '${latestCap.bedsAvailable ?? '-'}'),
                              _kv('Oxygen', '${latestCap.oxygenUnits ?? '-'}'),
                              _kv('Ambulances', '${latestCap.ambulancesAvailable ?? '-'}'),
                            ],
                          ),
                  ),
                ],
              );
            },
          ),
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

String _fmtDurationSeconds(double? seconds) {
  if (seconds == null) return '-';
  final s = seconds.round();
  if (s < 60) return '${s}s';
  final min = (s / 60).floor();
  final rem = s % 60;
  return rem == 0 ? '${min}m' : '${min}m ${rem}s';
}

Widget _kv(String k, String v) {
  return Padding(
    padding: const EdgeInsets.only(bottom: 6),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Text(
            k,
            style: AppTextStyles.bodyMuted(),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
        const SizedBox(width: 8),
        Text(
          v,
          style: AppTextStyles.body().copyWith(fontWeight: FontWeight.w600),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
      ],
    ),
  );
}

class _KpiCard extends StatelessWidget {
  const _KpiCard({required this.title, required this.value});

  final String title;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: AppTextStyles.bodyMuted(),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 6),
          Text(
            value,
            style: AppTextStyles.titleMedium().copyWith(fontSize: 18, fontWeight: FontWeight.w700),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: AppTextStyles.titleMedium().copyWith(fontSize: 15),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 8),
          child,
        ],
      ),
    );
  }
}

class _IncidentsByZoneChart extends StatelessWidget {
  const _IncidentsByZoneChart({required this.items});

  final List<IncidentsByZoneDto> items;

  @override
  Widget build(BuildContext context) {
    final maxIncidents = items.fold<int>(0, (m, e) => e.incidents > m ? e.incidents : m);
    final safeMax = maxIncidents <= 0 ? 1 : maxIncidents;
    return Column(
      children: items
          .take(6)
          .map(
            (z) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          z.zoneId,
                          style: AppTextStyles.body(),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '${z.incidents}',
                        style: AppTextStyles.body().copyWith(fontWeight: FontWeight.w600),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(999),
                    child: LinearProgressIndicator(
                      value: z.incidents / safeMax,
                      minHeight: 8,
                      backgroundColor: AppColors.surfaceCanvas,
                      valueColor: const AlwaysStoppedAnimation<Color>(AppColors.primary),
                    ),
                  ),
                ],
              ),
            ),
          )
          .toList(growable: false),
    );
  }
}

class _AnalyticsLoading extends StatelessWidget {
  const _AnalyticsLoading();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: const Center(child: CircularProgressIndicator()),
    );
  }
}

class _AnalyticsError extends StatelessWidget {
  const _AnalyticsError({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Text(
        message,
        style: AppTextStyles.bodyMuted(),
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
