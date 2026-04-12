import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../data/admin_inspection_dtos.dart';
import '../providers/admin_inspection_providers.dart';
import '../widgets/admin_stat_card.dart';
import '../widgets/admin_section_header.dart';

class AdminInspectionScreen extends ConsumerStatefulWidget {
  const AdminInspectionScreen({super.key});

  @override
  ConsumerState<AdminInspectionScreen> createState() => _AdminInspectionScreenState();
}

class _AdminInspectionScreenState extends ConsumerState<AdminInspectionScreen> {
  DateTime? _lastUpdated;

  @override
  Widget build(BuildContext context) {
    final overview = ref.watch(adminOverviewProvider);
    ref.listen<AsyncValue<dynamic>>(adminOverviewProvider, (prev, next) {
      if (next.hasValue && !next.isLoading) {
        setState(() => _lastUpdated = DateTime.now());
      }
    });

    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Operations inspection'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(adminOverviewProvider);
          await ref.read(adminOverviewProvider.future);
        },
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 28),
          children: [
            Text(
              'Live graph snapshot',
              style: AppTextStyles.heroSupporting().copyWith(
                fontSize: 13,
                color: AppColors.textTertiary,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Data is read directly from Neo4j — use this during demos to prove persistence.',
              style: AppTextStyles.heroSupporting().copyWith(
                fontSize: 13,
                color: AppColors.textSecondary,
                height: 1.35,
              ),
            ),
            if (_lastUpdated != null) ...[
              const SizedBox(height: 6),
              Text(
                'Last updated ${_fmt(_lastUpdated!)}',
                style: AppTextStyles.heroSupporting().copyWith(
                  fontSize: 12,
                  color: AppColors.textTertiary,
                ),
              ),
            ],
            const SizedBox(height: 16),
            TextField(
              enabled: false,
              decoration: InputDecoration(
                labelText: 'Search',
                hintText: 'TODO: wire search across users, incidents, volunteers',
                border: const OutlineInputBorder(),
                isDense: true,
                prefixIcon: const Icon(Icons.search, size: 20),
              ),
            ),
            const SizedBox(height: 20),
            const AdminSectionHeader(
              title: 'Overview',
              subtitle: 'Counts match the live Neo4j graph.',
            ),
            overview.when(
              loading: () => const Padding(
                padding: EdgeInsets.all(24),
                child: Center(child: CircularProgressIndicator()),
              ),
              error: (e, _) => _OverviewError(
                message: e.toString(),
                onRetry: () => ref.invalidate(adminOverviewProvider),
              ),
              data: (o) => _OverviewGrid(o: o),
            ),
            const SizedBox(height: 24),
            const AdminSectionHeader(
              title: 'Directories',
              subtitle: 'Open a list for field operations review.',
            ),
            const SizedBox(height: 4),
            _NavTile(
              icon: Icons.people_outline,
              title: 'Users',
              subtitle: 'Registered affected users',
              onTap: () => context.push(AppRoutes.adminInspectionUsers),
            ),
            _NavTile(
              icon: Icons.volunteer_activism_outlined,
              title: 'Volunteers',
              subtitle: 'Trust, credits, assignments',
              onTap: () => context.push(AppRoutes.adminInspectionVolunteers),
            ),
            _NavTile(
              icon: Icons.warning_amber_outlined,
              title: 'Incidents',
              subtitle: 'Newest first, full graph-backed rows',
              onTap: () => context.push(AppRoutes.adminInspectionIncidents),
            ),
            _NavTile(
              icon: Icons.link,
              title: 'Assignments',
              subtitle: 'Volunteer ↔ incident edges',
              onTap: () => context.push(AppRoutes.adminInspectionAssignments),
            ),
            _NavTile(
              icon: Icons.card_giftcard_outlined,
              title: 'Rewards',
              subtitle: 'Credits and completion counts',
              onTap: () => context.push(AppRoutes.adminInspectionRewards),
            ),
            _NavTile(
              icon: Icons.map_outlined,
              title: 'Support network',
              subtitle: 'Hospitals, shelters, contacts, zones',
              onTap: () => context.push(AppRoutes.adminInspectionSupport),
            ),
          ],
        ),
      ),
    );
  }

  static String _fmt(DateTime d) {
    final t = TimeOfDay.fromDateTime(d);
    final h = t.hourOfPeriod == 0 ? 12 : t.hourOfPeriod;
    final m = t.minute.toString().padLeft(2, '0');
    final suffix = t.period == DayPeriod.am ? 'AM' : 'PM';
    return '$h:$m $suffix';
  }
}

class _OverviewGrid extends StatelessWidget {
  const _OverviewGrid({required this.o});

  final AdminOverviewDto o;

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 10,
      crossAxisSpacing: 10,
      childAspectRatio: 1.15,
      children: [
        AdminStatCard(label: 'Users', value: '${o.totalUsers}', icon: Icons.people_outline),
        AdminStatCard(label: 'Volunteers', value: '${o.totalVolunteers}', icon: Icons.groups_2_outlined),
        AdminStatCard(label: 'Active incidents', value: '${o.activeIncidents}', icon: Icons.bolt_outlined),
        AdminStatCard(label: 'Pending incidents', value: '${o.pendingIncidents}', icon: Icons.hourglass_empty),
        AdminStatCard(label: 'Resolved incidents', value: '${o.resolvedIncidents}', icon: Icons.check_circle_outline),
        AdminStatCard(label: 'Hospitals', value: '${o.totalHospitals}', icon: Icons.local_hospital_outlined),
        AdminStatCard(label: 'Shelters', value: '${o.totalShelters}', icon: Icons.home_work_outlined),
        AdminStatCard(
          label: 'Volunteer credits (sum)',
          value: '${o.totalVolunteerCredits}',
          icon: Icons.stars_outlined,
        ),
        AdminStatCard(
          label: 'Avg trust (volunteers)',
          value: o.averageVolunteerTrustScore.toStringAsFixed(2),
          icon: Icons.verified_user_outlined,
        ),
      ],
    );
  }
}

class _OverviewError extends StatelessWidget {
  const _OverviewError({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Could not load overview',
              style: AppTextStyles.heroSupporting().copyWith(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Text(
              message.replaceFirst('Exception: ', ''),
              style: AppTextStyles.heroSupporting().copyWith(fontSize: 13, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 12),
            FilledButton.tonal(onPressed: onRetry, child: const Text('Retry')),
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
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Material(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
            child: Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: AppColors.iconSoftFill,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(icon, color: AppColors.primary),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: AppTextStyles.heroSupporting().copyWith(
                          fontWeight: FontWeight.w600,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        subtitle,
                        style: AppTextStyles.heroSupporting().copyWith(
                          fontSize: 12,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.chevron_right, color: AppColors.textTertiary),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
