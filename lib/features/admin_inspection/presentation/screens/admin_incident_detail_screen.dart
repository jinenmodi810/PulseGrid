import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../data/admin_inspection_dtos.dart';
import '../providers/admin_inspection_providers.dart';
import '../widgets/admin_empty_state.dart';
import '../widgets/admin_section_header.dart';

class AdminIncidentDetailScreen extends ConsumerWidget {
  const AdminIncidentDetailScreen({super.key, required this.incidentId});

  final String incidentId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(adminIncidentDetailProvider(incidentId));
    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Incident inspection'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(adminIncidentDetailProvider(incidentId)),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(adminIncidentDetailProvider(incidentId));
          await ref.read(adminIncidentDetailProvider(incidentId).future);
        },
        child: async.when(
          loading: () => ListView(children: const [SizedBox(height: 120), Center(child: CircularProgressIndicator())]),
          error: (e, _) => ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            children: [
              AdminEmptyState(
                title: 'Could not load incident',
                message: e.toString().replaceFirst('Exception: ', ''),
                icon: Icons.cloud_off_outlined,
                actionLabel: 'Retry',
                onAction: () => ref.invalidate(adminIncidentDetailProvider(incidentId)),
              ),
            ],
          ),
          data: (d) => _DetailBody(d: d),
        ),
      ),
    );
  }
}

class _DetailBody extends StatelessWidget {
  const _DetailBody({required this.d});

  final AdminIncidentDetailDto d;

  @override
  Widget build(BuildContext context) {
    final inc = d.incident;
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
      children: [
        const AdminSectionHeader(title: 'Summary', subtitle: 'Core incident properties'),
        _CardBlock(
          children: [
            _kv('Type', inc.incidentType),
            _kv('Status', inc.status),
            _kv('Severity', inc.severity),
            _kv('Priority', '${inc.priorityLabel} (${inc.priorityScore.toStringAsFixed(1)})'),
            _kv('Zone', inc.zoneId),
            _kv('People', '${inc.peopleCount}'),
            if (inc.createdAt != null) _kv('Created', inc.createdAt!),
            _kv('Route (graph)', d.routeStatus),
          ],
        ),
        const SizedBox(height: 20),
        const AdminSectionHeader(title: 'Reporting user', subtitle: 'REPORTED edge'),
        _CardBlock(
          children: d.reportingUser == null || d.reportingUser!.userId.isEmpty
              ? [Text('No reporter linked', style: _muted(context))]
              : [
                  _kv('User ID', d.reportingUser!.userId),
                  _kv('Name', d.reportingUser!.name),
                  _kv('Phone', d.reportingUser!.phone),
                  _kv('Home zone', d.reportingUser!.zoneId),
                ],
        ),
        const SizedBox(height: 20),
        const AdminSectionHeader(title: 'Assigned volunteer', subtitle: 'ASSIGNED_TO edge'),
        _CardBlock(
          children: d.assignedVolunteer == null || d.assignedVolunteer!.volunteerId.isEmpty
              ? [Text('No assignee on graph', style: _muted(context))]
              : [
                  _kv('Volunteer ID', d.assignedVolunteer!.volunteerId),
                  _kv('Name', d.assignedVolunteer!.name),
                  _kv('Phone', d.assignedVolunteer!.phone),
                ],
        ),
        const SizedBox(height: 20),
        const AdminSectionHeader(title: 'Zone (LOCATED_IN)', subtitle: 'Optional graph zone node'),
        _CardBlock(
          children: d.zone == null || d.zone!.zoneId.isEmpty
              ? [Text('No zone node (check flat zone_id on incident)', style: _muted(context))]
              : [
                  _kv('Zone ID', d.zone!.zoneId),
                  _kv('Name', d.zone!.name),
                ],
        ),
        const SizedBox(height: 20),
        const AdminSectionHeader(title: 'Needs & flags', subtitle: 'What the field should verify'),
        _CardBlock(
          children: [
            _boolRow('Elderly', inc.elderly),
            _boolRow('Child present', inc.childPresent),
            _boolRow('Injury', inc.injury),
            _boolRow('Oxygen', inc.oxygenRequired),
            _boolRow('Shelter', inc.shelterNeeded),
            _boolRow('Food', inc.foodNeeded),
            _boolRow('Transport', inc.transportNeeded),
            if (inc.note.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text('Note', style: _label(context)),
              const SizedBox(height: 4),
              Text(inc.note, style: AppTextStyles.heroSupporting().copyWith(color: AppColors.textPrimary)),
            ],
          ],
        ),
        const SizedBox(height: 20),
        const AdminSectionHeader(title: 'AI guidance', subtitle: 'Stored on incident node'),
        _CardBlock(
          children: [
            Text(
              d.aiGuidance.isEmpty ? '—' : d.aiGuidance,
              style: AppTextStyles.heroSupporting().copyWith(height: 1.35),
            ),
          ],
        ),
        const SizedBox(height: 20),
        const AdminSectionHeader(
          title: 'Matching rejections',
          subtitle: 'Parsed from rejected_json',
        ),
        _CardBlock(
          children: d.rejectedCandidates.isEmpty
              ? [Text('None recorded', style: _muted(context))]
              : d.rejectedCandidates
                  .map<Widget>(
                    (r) => Padding(
                      padding: const EdgeInsets.only(bottom: 10),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(r.name.isNotEmpty ? r.name : r.volunteerId, style: _label(context)),
                          if (r.reason.isNotEmpty)
                            Text(r.reason, style: AppTextStyles.heroSupporting().copyWith(fontSize: 13)),
                        ],
                      ),
                    ),
                  )
                  .toList(),
        ),
        const SizedBox(height: 20),
        const AdminSectionHeader(
          title: 'Status & task timeline',
          subtitle: 'Synthesized from graph; TODO: dedicated history nodes',
        ),
        _CardBlock(
          children: d.statusHistory.isEmpty
              ? [Text('No timeline entries', style: _muted(context))]
              : d.statusHistory.map<Widget>((row) {
                  final parts = row.entries.map((e) => '${e.key}: ${e.value}').join(' · ');
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Text(parts, style: AppTextStyles.heroSupporting().copyWith(fontSize: 13, height: 1.3)),
                  );
                }).toList(),
        ),
        const SizedBox(height: 20),
        const AdminSectionHeader(title: 'Graph relationships', subtitle: 'Readable edge summary'),
        _CardBlock(
          children: [
            SelectableText(
              d.relationshipsSummary.isEmpty ? 'No additional edges found.' : d.relationshipsSummary,
              style: AppTextStyles.heroSupporting().copyWith(fontSize: 12, height: 1.35),
            ),
          ],
        ),
      ],
    );
  }

  static TextStyle _muted(BuildContext context) =>
      AppTextStyles.heroSupporting().copyWith(color: AppColors.textSecondary);

  static TextStyle _label(BuildContext context) =>
      AppTextStyles.heroSupporting().copyWith(fontWeight: FontWeight.w600, fontSize: 12);

  static Widget _kv(String k, String v) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 108,
            child: Text(
              k,
              style: AppTextStyles.heroSupporting().copyWith(
                fontSize: 12,
                color: AppColors.textTertiary,
              ),
            ),
          ),
          Expanded(
            child: Text(
              v.isEmpty ? '—' : v,
              style: AppTextStyles.heroSupporting().copyWith(fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }

  static Widget _boolRow(String label, bool on) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          Icon(on ? Icons.check_circle : Icons.remove_circle_outline, size: 18, color: on ? AppColors.success : AppColors.textTertiary),
          const SizedBox(width: 8),
          Expanded(child: Text(label, style: AppTextStyles.heroSupporting().copyWith(fontSize: 13))),
        ],
      ),
    );
  }
}

class _CardBlock extends StatelessWidget {
  const _CardBlock({required this.children});

  final List<Widget> children;

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
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: children),
    );
  }
}
