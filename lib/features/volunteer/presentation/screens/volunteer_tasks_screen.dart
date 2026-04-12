import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/providers.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/utils/result.dart';
import '../../../../core/widgets/empty_state.dart';
import '../../../../core/widgets/loading_view.dart';
import '../providers/volunteer_realtime_provider.dart';
import '../providers/volunteer_task_providers.dart';
import '../widgets/task_card.dart';

Future<void> _acceptVolunteerTask(WidgetRef ref, BuildContext context, String incidentId) async {
  final storage = ref.read(storageServiceProvider);
  final vid = await storage.getString(SessionKeys.graphVolunteerId);
  if (!context.mounted) return;
  if (vid == null || vid.isEmpty) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Volunteer session not found.')),
    );
    return;
  }
  final result = await ref.read(acceptTaskUsecaseProvider).call(incidentId: incidentId, volunteerId: vid);
  if (!context.mounted) return;
  switch (result) {
    case Success():
      invalidateVolunteerTaskCaches(ref, incidentId: incidentId);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Task accepted.')));
    case Failure(:final error):
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
  }
}

class VolunteerTasksScreen extends ConsumerWidget {
  const VolunteerTasksScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.watch(volunteerRealtimeBySessionProvider);
    final tasksAsync = ref.watch(volunteerTasksForSessionProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Open tasks near you'),
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
        actions: [
          IconButton(
            tooltip: 'Rewards',
            icon: const Icon(Icons.workspace_premium_outlined),
            onPressed: () => context.push(AppRoutes.rewards),
          ),
          IconButton(
            tooltip: 'Profile',
            icon: const Icon(Icons.person_outline),
            onPressed: () => context.push(AppRoutes.profile),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(volunteerTasksForSessionProvider);
          await ref.read(volunteerTasksForSessionProvider.future);
        },
        child: tasksAsync.when(
          loading: () => ListView(
                children: const [
                  SizedBox(height: 120),
                  LoadingView(message: 'Loading tasks…'),
                ],
              ),
          error: (e, _) => ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(24),
            children: [
              EmptyState(
                title: 'Could not load tasks',
                message: e.toString().replaceFirst('Exception: ', ''),
                actionLabel: 'Retry',
                onAction: () => ref.invalidate(volunteerTasksForSessionProvider),
              ),
            ],
          ),
          data: (tasks) {
            if (tasks.isEmpty) {
              return ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(24),
                children: [
                  EmptyState(
                    title: 'No tasks right now',
                    message:
                        'When incidents are assigned to you or open in your zone, they will appear here.',
                    actionLabel: 'Refresh',
                    onAction: () => ref.invalidate(volunteerTasksForSessionProvider),
                  ),
                ],
              );
            }
            return ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              children: [
                Text('Your queue', style: AppTextStyles.titleMedium()),
                const SizedBox(height: 6),
                Text(
                  // TODO(Phase1C+): push task updates over websocket instead of pull-to-refresh.
                  'Pull down to refresh. Tap a card for full details.',
                  style: AppTextStyles.bodyMuted(),
                ),
                const SizedBox(height: 14),
                for (final t in tasks) ...[
                  TaskCard(
                    task: t,
                    onOpenDetail: () => context.push(AppRoutes.volunteerTaskDetail(t.incidentId)),
                    onAccept: () => _acceptVolunteerTask(ref, context, t.incidentId),
                  ),
                  const SizedBox(height: 10),
                ],
              ],
            );
          },
        ),
      ),
    );
  }
}
