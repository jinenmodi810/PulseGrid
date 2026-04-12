import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../providers/organization_providers.dart';

class OrganizationProfileScreen extends ConsumerWidget {
  const OrganizationProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final o = ref.watch(organizationOverviewProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Organization profile'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: o.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text(e.toString())),
        data: (org) => ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text(org.name, style: AppTextStyles.titleMedium().copyWith(fontSize: 22)),
            const SizedBox(height: 8),
            Text('Type: ${org.orgType}', style: AppTextStyles.body()),
            Text('Zone: ${org.zoneId}', style: AppTextStyles.body()),
            Text('Organization id: ${org.organizationId}', style: AppTextStyles.microcopy()),
            const SizedBox(height: 20),
            Text('Capacity snapshot', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
            const SizedBox(height: 8),
            ...org.capacity.entries.map((e) => Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Text('${e.key}: ${e.value}', style: AppTextStyles.bodyMuted()),
                )),
          ],
        ),
      ),
    );
  }
}
