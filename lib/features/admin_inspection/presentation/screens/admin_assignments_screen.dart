import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/theme/app_colors.dart';
import '../../data/admin_inspection_dtos.dart';
import '../providers/admin_inspection_providers.dart';
import '../widgets/admin_empty_state.dart';
import '../widgets/admin_entity_list_tile.dart';
import '../widgets/admin_section_header.dart';

class AdminAssignmentsScreen extends ConsumerWidget {
  const AdminAssignmentsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(adminAssignmentsProvider);
    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Assignments'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(adminAssignmentsProvider);
          await ref.read(adminAssignmentsProvider.future);
        },
        child: async.when(
          loading: () => ListView(children: const [SizedBox(height: 120), Center(child: CircularProgressIndicator())]),
          error: (e, _) => ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            children: [
              AdminEmptyState(
                title: 'Could not load assignments',
                message: e.toString().replaceFirst('Exception: ', ''),
                icon: Icons.cloud_off_outlined,
                actionLabel: 'Retry',
                onAction: () => ref.invalidate(adminAssignmentsProvider),
              ),
            ],
          ),
          data: (list) => _AssignmentsBody(assignments: list),
        ),
      ),
    );
  }
}

class _AssignmentsBody extends StatelessWidget {
  const _AssignmentsBody({required this.assignments});

  final List<AdminAssignmentDto> assignments;

  @override
  Widget build(BuildContext context) {
    if (assignments.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: const [
          AdminEmptyState(
            title: 'No ASSIGNED_TO edges',
            message: 'When matching assigns a volunteer, rows appear here.',
            icon: Icons.link_off,
          ),
        ],
      );
    }
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
      itemCount: assignments.length + 2,
      separatorBuilder: (_, _) => const SizedBox(height: 8),
      itemBuilder: (context, i) {
        if (i == 0) {
          return const AdminSectionHeader(
            title: 'Volunteer → incident',
            subtitle: 'TODO: filter by zone',
          );
        }
        if (i == 1) {
          return TextField(
            enabled: false,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              hintText: 'TODO: search assignments',
              prefixIcon: Icon(Icons.search, size: 20),
            ),
          );
        }
        final a = assignments[i - 2];
        return AdminEntityListTile(
          leadingIcon: Icons.assignment_ind,
          title: a.volunteerName.isEmpty ? a.volunteerId : a.volunteerName,
          subtitle: [
            'Incident ${a.incidentId}',
            a.status.toUpperCase(),
            if (a.priorityLabel.isNotEmpty) a.priorityLabel,
            if (a.zoneId.isNotEmpty) 'Zone ${a.zoneId}',
            if (a.assignedAt != null) 'Accepted ${a.assignedAt}',
          ].where((s) => s.isNotEmpty).join(' · '),
          trailing: const Icon(Icons.chevron_right, color: AppColors.textTertiary),
          onTap: () => context.push(AppRoutes.adminInspectionIncidentDetail(a.incidentId)),
        );
      },
    );
  }
}
