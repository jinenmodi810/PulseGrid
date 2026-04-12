import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/theme/app_colors.dart';
import '../../data/admin_inspection_dtos.dart';
import '../providers/admin_inspection_providers.dart';
import '../widgets/admin_empty_state.dart';
import '../widgets/admin_entity_list_tile.dart';
import '../widgets/admin_section_header.dart';

class AdminRewardsScreen extends ConsumerWidget {
  const AdminRewardsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(adminRewardsProvider);
    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Rewards'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(adminRewardsProvider);
          await ref.read(adminRewardsProvider.future);
        },
        child: async.when(
          loading: () => ListView(children: const [SizedBox(height: 120), Center(child: CircularProgressIndicator())]),
          error: (e, _) => ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            children: [
              AdminEmptyState(
                title: 'Could not load rewards',
                message: e.toString().replaceFirst('Exception: ', ''),
                icon: Icons.cloud_off_outlined,
                actionLabel: 'Retry',
                onAction: () => ref.invalidate(adminRewardsProvider),
              ),
            ],
          ),
          data: (list) => _RewardsBody(rewards: list),
        ),
      ),
    );
  }
}

class _RewardsBody extends StatelessWidget {
  const _RewardsBody({required this.rewards});

  final List<AdminRewardDto> rewards;

  @override
  Widget build(BuildContext context) {
    if (rewards.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: const [
          AdminEmptyState(
            title: 'No volunteers',
            message: 'Nothing to rank yet.',
            icon: Icons.emoji_events_outlined,
          ),
        ],
      );
    }
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
      itemCount: rewards.length + 2,
      separatorBuilder: (_, _) => const SizedBox(height: 8),
      itemBuilder: (context, i) {
        if (i == 0) {
          return const AdminSectionHeader(
            title: 'Volunteer reward state',
            subtitle: 'EARNED_REWARD count + COMPLETED_TASK incidents',
          );
        }
        if (i == 1) {
          return TextField(
            enabled: false,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              hintText: 'TODO: filter by min credits',
              prefixIcon: Icon(Icons.search, size: 20),
            ),
          );
        }
        final r = rewards[i - 2];
        return AdminEntityListTile(
          leadingIcon: Icons.stars_outlined,
          title: r.volunteerName.isEmpty ? r.volunteerId : r.volunteerName,
          subtitle:
              'Credits ${r.credits} · Trust ${r.trustScore.toStringAsFixed(2)} · Rewards ${r.earnedRewardCount} · Completed ${r.completedIncidentCount}',
        );
      },
    );
  }
}
