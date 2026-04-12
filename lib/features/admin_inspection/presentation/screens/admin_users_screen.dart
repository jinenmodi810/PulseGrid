import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/theme/app_colors.dart';
import '../../data/admin_inspection_dtos.dart';
import '../providers/admin_inspection_providers.dart';
import '../widgets/admin_empty_state.dart';
import '../widgets/admin_entity_list_tile.dart';
import '../widgets/admin_section_header.dart';

class AdminUsersScreen extends ConsumerWidget {
  const AdminUsersScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(adminUsersProvider);
    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Users'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(adminUsersProvider);
          await ref.read(adminUsersProvider.future);
        },
        child: async.when(
          loading: () => ListView(children: const [SizedBox(height: 120), Center(child: CircularProgressIndicator())]),
          error: (e, _) => ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            children: [
              AdminEmptyState(
                title: 'Could not load users',
                message: e.toString().replaceFirst('Exception: ', ''),
                icon: Icons.cloud_off_outlined,
                actionLabel: 'Retry',
                onAction: () => ref.invalidate(adminUsersProvider),
              ),
            ],
          ),
          data: (users) => _UsersBody(users: users),
        ),
      ),
    );
  }
}

class _UsersBody extends StatelessWidget {
  const _UsersBody({required this.users});

  final List<AdminUserDto> users;

  @override
  Widget build(BuildContext context) {
    if (users.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: const [
          AdminEmptyState(
            title: 'No users in graph',
            message: 'Register an affected user from the app to see rows here.',
            icon: Icons.person_off_outlined,
          ),
        ],
      );
    }
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
      itemCount: users.length + 2,
      separatorBuilder: (_, _) => const SizedBox(height: 8),
      itemBuilder: (context, i) {
        if (i == 0) {
          return const AdminSectionHeader(
            title: 'Registered users',
            subtitle: 'TODO: filters & pagination',
          );
        }
        if (i == 1) {
          return TextField(
            enabled: false,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              hintText: 'TODO: search by name or phone',
              prefixIcon: Icon(Icons.search, size: 20),
            ),
          );
        }
        final u = users[i - 2];
        return AdminEntityListTile(
          leadingIcon: Icons.person_outline,
          title: u.name.isEmpty ? u.userId : u.name,
          subtitle: [
            if (u.phone.isNotEmpty) u.phone,
            if (u.zoneId.isNotEmpty) 'Zone ${u.zoneId}',
            if (u.language.isNotEmpty) u.language,
            if (u.familySize != null) 'Family size ${u.familySize}',
            if (u.createdAt != null) u.createdAt!,
          ].where((s) => s.isNotEmpty).join(' · '),
        );
      },
    );
  }
}
