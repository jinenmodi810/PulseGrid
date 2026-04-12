import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../providers/admin_inspection_providers.dart';
import '../widgets/admin_empty_state.dart';
import '../widgets/admin_entity_list_tile.dart';
import '../widgets/admin_section_header.dart';

class AdminSupportNetworkScreen extends ConsumerWidget {
  const AdminSupportNetworkScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(adminSupportNetworkProvider);
    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Support network'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(adminSupportNetworkProvider);
          await ref.read(adminSupportNetworkProvider.future);
        },
        child: async.when(
          loading: () => ListView(children: const [SizedBox(height: 120), Center(child: CircularProgressIndicator())]),
          error: (e, _) => ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            children: [
              AdminEmptyState(
                title: 'Could not load support network',
                message: e.toString().replaceFirst('Exception: ', ''),
                icon: Icons.cloud_off_outlined,
                actionLabel: 'Retry',
                onAction: () => ref.invalidate(adminSupportNetworkProvider),
              ),
            ],
          ),
          data: (net) => ListView(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
            children: [
              Text(
                'Hospital, shelter, contact, and zone nodes as stored in Neo4j.',
                style: AppTextStyles.heroSupporting().copyWith(fontSize: 13, color: AppColors.textSecondary),
              ),
              const SizedBox(height: 16),
              const AdminSectionHeader(title: 'Hospitals'),
              ..._mapProps(net.hospitals, Icons.local_hospital_outlined),
              const SizedBox(height: 16),
              const AdminSectionHeader(title: 'Shelters'),
              ..._mapProps(net.shelters, Icons.home_work_outlined),
              const SizedBox(height: 16),
              const AdminSectionHeader(title: 'Support contacts'),
              ..._mapProps(net.supportContacts, Icons.support_agent),
              const SizedBox(height: 16),
              const AdminSectionHeader(title: 'Zones'),
              ...net.zones.map(
                (z) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: AdminEntityListTile(
                    leadingIcon: Icons.map_outlined,
                    title: (z['name'] ?? z['zone_id'] ?? '').toString(),
                    subtitle: 'ID ${z['zone_id'] ?? ''}',
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  static List<Widget> _mapProps(List<Map<String, dynamic>> rows, IconData icon) {
    if (rows.isEmpty) {
      return [
        Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Text('None', style: AppTextStyles.heroSupporting().copyWith(color: AppColors.textTertiary)),
        ),
      ];
    }
    return rows.map((props) {
      final title = (props['name'] ?? props['id'] ?? props['title'] ?? 'Record').toString();
      final subtitle = props.entries
          .where((e) => e.value != null && '${e.value}'.isNotEmpty)
          .take(5)
          .map((e) => '${e.key}: ${e.value}')
          .join(' · ');
      return Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: AdminEntityListTile(
          leadingIcon: icon,
          title: title,
          subtitle: subtitle,
        ),
      );
    }).toList();
  }
}
