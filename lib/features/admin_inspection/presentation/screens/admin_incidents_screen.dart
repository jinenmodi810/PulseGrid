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

class AdminIncidentsScreen extends ConsumerWidget {
  const AdminIncidentsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(adminIncidentsProvider);
    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Incidents'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(adminIncidentsProvider);
          await ref.read(adminIncidentsProvider.future);
        },
        child: async.when(
          loading: () => ListView(children: const [SizedBox(height: 120), Center(child: CircularProgressIndicator())]),
          error: (e, _) => ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            children: [
              AdminEmptyState(
                title: 'Could not load incidents',
                message: e.toString().replaceFirst('Exception: ', ''),
                icon: Icons.cloud_off_outlined,
                actionLabel: 'Retry',
                onAction: () => ref.invalidate(adminIncidentsProvider),
              ),
            ],
          ),
          data: (list) => _IncidentsBody(incidents: list),
        ),
      ),
    );
  }
}

class _IncidentsBody extends StatelessWidget {
  const _IncidentsBody({required this.incidents});

  final List<AdminIncidentDto> incidents;

  @override
  Widget build(BuildContext context) {
    if (incidents.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: const [
          AdminEmptyState(
            title: 'No incidents',
            message: 'Submit a help request to create incident nodes.',
            icon: Icons.crisis_alert_outlined,
          ),
        ],
      );
    }
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
      itemCount: incidents.length + 2,
      separatorBuilder: (_, _) => const SizedBox(height: 8),
      itemBuilder: (context, i) {
        if (i == 0) {
          return const AdminSectionHeader(
            title: 'All incidents',
            subtitle: 'Newest first · TODO: status filters',
          );
        }
        if (i == 1) {
          return TextField(
            enabled: false,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              hintText: 'TODO: search incidents',
              prefixIcon: Icon(Icons.search, size: 20),
            ),
          );
        }
        final inc = incidents[i - 2];
        return AdminEntityListTile(
          leadingIcon: Icons.warning_amber_outlined,
          title: inc.incidentType.isEmpty ? inc.incidentId : inc.incidentType,
          subtitle: [
            inc.status.toUpperCase(),
            inc.priorityLabel,
            if (inc.zoneId.isNotEmpty) 'Zone ${inc.zoneId}',
            if (inc.createdAt != null) inc.createdAt!,
          ].join(' · '),
          trailing: const Icon(Icons.chevron_right, color: AppColors.textTertiary),
          onTap: () => context.push(AppRoutes.adminInspectionIncidentDetail(inc.incidentId)),
        );
      },
    );
  }
}
