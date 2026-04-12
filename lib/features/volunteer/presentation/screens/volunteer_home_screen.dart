import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/layout/screen_insets.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../auth/presentation/utils/session_navigation.dart';
import '../../../profile/presentation/widgets/trust_score_card.dart';
import '../providers/volunteer_realtime_provider.dart';
import '../providers/volunteer_task_providers.dart';
import '../../data/volunteer_task_item_dto.dart';

class VolunteerHomeScreen extends ConsumerWidget {
  const VolunteerHomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.watch(volunteerRealtimeBySessionProvider);
    final tasksAsync = ref.watch(volunteerTasksForSessionProvider);
    final profileAsync = ref.watch(volunteerProfileBySessionProvider);

    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Responder home'),
        automaticallyImplyLeading: false,
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) async {
              switch (value) {
                case 'tasks':
                  context.push(AppRoutes.volunteerTasks);
                  break;
                case 'rewards':
                  context.push(AppRoutes.rewards);
                  break;
                case 'profile':
                  context.push(AppRoutes.profile);
                  break;
                case 'signout':
                  await signOutAndGoLanding(ref, context);
                  break;
              }
            },
            itemBuilder: (context) => const [
              PopupMenuItem(value: 'tasks', child: Text('Nearby tasks')),
              PopupMenuItem(value: 'rewards', child: Text('Recognition')),
              PopupMenuItem(value: 'profile', child: Text('Your profile')),
              PopupMenuDivider(),
              PopupMenuItem(value: 'signout', child: Text('Sign out')),
            ],
          ),
        ],
      ),
      body: SafeArea(
        top: false,
        child: ListView(
          keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
          padding: ScreenInsets.listVertical(context),
          children: [
          Text(
            'Stay ready. Urgent work is highlighted first.',
            style: AppTextStyles.heroSupporting(),
            maxLines: 4,
            overflow: TextOverflow.fade,
            softWrap: true,
          ),
          const SizedBox(height: 20),
          profileAsync.when(
            data: (v) {
              if (v == null) {
                return Text('Profile unavailable', style: AppTextStyles.bodyMuted());
              }
              return _ProfileSnapshotCard(profile: v);
            },
            loading: () => const Center(child: Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator())),
            error: (_, __) => const SizedBox.shrink(),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: FilledButton.tonalIcon(
                  onPressed: () => context.push(AppRoutes.volunteerTasks),
                  icon: const Icon(Icons.list_alt_outlined),
                  label: Text(
                    'Task feed',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: AppTextStyles.body().copyWith(fontSize: 13),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () => context.push(AppRoutes.rewards),
                  icon: const Icon(Icons.workspace_premium_outlined),
                  label: Text(
                    'Credits',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: AppTextStyles.body().copyWith(fontSize: 13),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            'Your queue',
            style: AppTextStyles.titleMedium().copyWith(fontSize: 17),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 10),
          tasksAsync.when(
            data: (tasks) {
              final assigned = tasks.where((t) => t.taskSource.toLowerCase() == 'assigned').toList();
              final open = tasks.where((t) => t.taskSource.toLowerCase() != 'assigned').toList();
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (assigned.isNotEmpty) ...[
                    Text(
                      'Active assigned tasks',
                      style: AppTextStyles.body().copyWith(fontWeight: FontWeight.w600),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    ...assigned.take(4).map((t) => _TaskRow(task: t)),
                    if (assigned.length > 4)
                      TextButton(
                        onPressed: () => context.push(AppRoutes.volunteerTasks),
                        child: Text('View all (${assigned.length})'),
                      ),
                    const SizedBox(height: 16),
                  ],
                  Text(
                    'Nearby tasks',
                    style: AppTextStyles.body().copyWith(fontWeight: FontWeight.w600),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  if (open.isEmpty)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text(
                        'No open tasks in your zone right now. Check the feed for updates.',
                        style: AppTextStyles.bodyMuted(),
                        maxLines: 4,
                        overflow: TextOverflow.fade,
                        softWrap: true,
                      ),
                    )
                  else
                    ...open.take(5).map((t) => _TaskRow(task: t)),
                ],
              );
            },
            loading: () => const Padding(
              padding: EdgeInsets.symmetric(vertical: 24),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (e, _) => Text(
              e.toString().replaceFirst('Exception: ', ''),
              style: AppTextStyles.bodyMuted(),
              maxLines: 6,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
        ),
      ),
    );
  }
}

class _ProfileSnapshotCard extends StatelessWidget {
  const _ProfileSnapshotCard({required this.profile});

  final VolunteerProfileDto profile;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderSubtle),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.03), blurRadius: 10, offset: const Offset(0, 3)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            profile.displayName.isEmpty ? 'Responder' : profile.displayName,
            style: AppTextStyles.titleMedium().copyWith(fontSize: 18),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 6),
          if (profile.zoneId.isNotEmpty)
            Text(
              'Zone ${profile.zoneId}',
              style: AppTextStyles.bodyMuted(),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          if (profile.availability.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              'Availability: ${profile.availability}',
              style: AppTextStyles.bodyMuted(),
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
          ],
          const SizedBox(height: 12),
          TrustScoreCard(score: profile.trustScore.clamp(0.0, 1.0)),
          const SizedBox(height: 10),
          Text(
            'Credits: ${profile.credits}',
            style: AppTextStyles.body().copyWith(fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }
}

class _TaskRow extends StatelessWidget {
  const _TaskRow({required this.task});

  final VolunteerTaskItemDto task;

  @override
  Widget build(BuildContext context) {
    final urgent = task.priorityLabel.toUpperCase().contains('HIGH') || task.priorityScore >= 0.75;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Material(
        color: urgent ? AppColors.danger.withValues(alpha: 0.06) : AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          onTap: () => context.push(AppRoutes.volunteerTaskDetail(task.incidentId)),
          borderRadius: BorderRadius.circular(12),
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: urgent ? AppColors.danger.withValues(alpha: 0.35) : AppColors.border),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  task.incidentType,
                  style: AppTextStyles.body().copyWith(fontWeight: FontWeight.w600),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  '${task.priorityLabel} · ${task.status}',
                  style: AppTextStyles.microcopy(),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
