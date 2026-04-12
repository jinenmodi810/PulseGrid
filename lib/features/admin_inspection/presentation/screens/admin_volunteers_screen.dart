import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/theme/app_colors.dart';
import '../../data/admin_inspection_dtos.dart';
import '../providers/admin_inspection_providers.dart';
import '../widgets/admin_empty_state.dart';
import '../widgets/admin_entity_list_tile.dart';
import '../widgets/admin_section_header.dart';

class AdminVolunteersScreen extends ConsumerWidget {
  const AdminVolunteersScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(adminVolunteersProvider);
    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Volunteers'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(adminVolunteersProvider);
          await ref.read(adminVolunteersProvider.future);
        },
        child: async.when(
          loading: () => ListView(children: const [SizedBox(height: 120), Center(child: CircularProgressIndicator())]),
          error: (e, _) => ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            children: [
              AdminEmptyState(
                title: 'Could not load volunteers',
                message: e.toString().replaceFirst('Exception: ', ''),
                icon: Icons.cloud_off_outlined,
                actionLabel: 'Retry',
                onAction: () => ref.invalidate(adminVolunteersProvider),
              ),
            ],
          ),
          data: (list) => _VolunteersBody(volunteers: list),
        ),
      ),
    );
  }
}

class _VolunteersBody extends StatelessWidget {
  const _VolunteersBody({required this.volunteers});

  final List<AdminVolunteerDto> volunteers;

  @override
  Widget build(BuildContext context) {
    if (volunteers.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: const [
          AdminEmptyState(
            title: 'No volunteers',
            message: 'Register a volunteer to populate this list.',
            icon: Icons.group_off_outlined,
          ),
        ],
      );
    }
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
      itemCount: volunteers.length + 2,
      separatorBuilder: (_, _) => const SizedBox(height: 8),
      itemBuilder: (context, i) {
        if (i == 0) {
          return const AdminSectionHeader(
            title: 'Volunteer roster',
            subtitle: 'Trust and credits reflect Neo4j properties.',
          );
        }
        if (i == 1) {
          return TextField(
            enabled: false,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              hintText: 'TODO: search volunteers',
              prefixIcon: Icon(Icons.search, size: 20),
            ),
          );
        }
        final v = volunteers[i - 2];
        final lang = v.languages.join(', ');
        return AdminEntityListTile(
          leadingIcon: Icons.volunteer_activism_outlined,
          title: v.name.isEmpty ? v.volunteerId : v.name,
          subtitle: [
            'Trust ${v.trustScore.toStringAsFixed(2)} · Credits ${v.credits}',
            if (v.zoneId.isNotEmpty) 'Zone ${v.zoneId}',
            if (v.availability.isNotEmpty) v.availability,
            if (v.skillType.isNotEmpty) v.skillType,
            if (lang.isNotEmpty) lang,
            'Assigned ${v.assignedIncidentCount} · Done ${v.completedIncidentCount}',
            if (v.verified) 'Verified',
          ].where((s) => s.isNotEmpty).join(' · '),
          trailing: v.verified
              ? Icon(Icons.verified, size: 20, color: AppColors.success)
              : Icon(Icons.circle_outlined, size: 20, color: AppColors.textTertiary),
        );
      },
    );
  }
}
