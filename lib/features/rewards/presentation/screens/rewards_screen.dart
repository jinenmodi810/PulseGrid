import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/providers.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../volunteer/presentation/providers/volunteer_realtime_provider.dart';
import '../../../volunteer/presentation/providers/volunteer_task_providers.dart';
import '../../../../core/enums/reward_badge_type.dart';
import '../../../../core/widgets/empty_state.dart';
import '../../../../core/widgets/loading_view.dart';
import '../widgets/badge_card.dart';
import '../widgets/credits_card.dart';
import '../widgets/reward_tile.dart';

class RewardsScreen extends ConsumerWidget {
  const RewardsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.watch(volunteerRealtimeBySessionProvider);
    final rewards = ref.watch(rewardsProvider);
    final volunteerProfile = ref.watch(volunteerProfileBySessionProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Rewards'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go(AppRoutes.volunteerHome);
            }
          },
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          volunteerProfile.when(
            data: (v) => CreditsCard(
              credits: v?.credits ?? 0,
              subtitle: v == null
                  ? 'Sign in as a volunteer to see live credits from Neo4j.'
                  : 'Live balance from your volunteer profile.',
            ),
            loading: () => const CreditsCard(credits: 0, subtitle: 'Loading credits…'),
            error: (_, _) => const CreditsCard(credits: 0, subtitle: 'Could not load volunteer profile.'),
          ),
          const SizedBox(height: 12),
          const BadgeCard(title: 'Community Helper', badgeType: RewardBadgeType.bronze),
          const SizedBox(height: 16),
          Text('Catalog', style: AppTextStyles.titleMedium()),
          const SizedBox(height: 8),
          rewards.when(
            data: (items) {
              if (items.isEmpty) {
                return const EmptyState(
                  title: 'No reward catalog entries',
                  message:
                      'None returned from the API. Seed Reward nodes in Neo4j or insert rows so GET /rewards/ can populate this list.',
                );
              }
              return Column(
                children: items
                    .map(
                      (r) => Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: RewardTile(title: r.title, description: r.description),
                      ),
                    )
                    .toList(),
              );
            },
            loading: () => const LoadingView(message: 'Loading rewards…'),
            error: (error, _) => EmptyState(
              title: 'Could not load rewards',
              message: error.toString(),
              actionLabel: 'Retry',
              onAction: () => ref.invalidate(rewardsProvider),
            ),
          ),
        ],
      ),
    );
  }
}
