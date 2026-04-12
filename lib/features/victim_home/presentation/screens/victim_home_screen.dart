import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/layout/screen_insets.dart';
import '../../../../core/widgets/app_button.dart';
import '../../../auth/presentation/providers/auth_providers.dart';
import '../../../auth/presentation/utils/session_navigation.dart';
import '../../../help_request/presentation/providers/help_request_providers.dart';
import '../../../incident_tracking/presentation/providers/incident_realtime_provider.dart';

bool _incidentStillActive(String status) {
  final s = status.toLowerCase();
  return s != 'resolved' && s != 'closed' && s != 'cancelled';
}

class VictimHomeScreen extends ConsumerWidget {
  const VictimHomeScreen({super.key});

  String _firstName(String fullName) {
    final t = fullName.trim();
    if (t.isEmpty) return '';
    return t.split(RegExp(r'\s+')).first;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(victimProfileBySessionProvider);
    final lastIdAsync = ref.watch(victimLastIncidentIdProvider);
    final lastId = lastIdAsync.when(
      data: (v) => v,
      error: (_, __) => null,
      loading: () => null,
    );
    if (lastId != null && lastId.isNotEmpty) {
      ref.watch(incidentRealtimeProvider(lastId));
    }

    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Home'),
        automaticallyImplyLeading: false,
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) async {
              switch (value) {
                case 'profile':
                  context.push(AppRoutes.profile);
                  break;
                case 'support':
                  context.push(AppRoutes.supportDirectory);
                  break;
                case 'signout':
                  await signOutAndGoLanding(ref, context);
                  break;
              }
            },
            itemBuilder: (context) => const [
              PopupMenuItem(value: 'support', child: Text('Trusted support')),
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
          profileAsync.when(
            data: (p) {
              final name = p?.fullName ?? '';
              final greet = _firstName(name);
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    greet.isEmpty ? 'You are not alone' : 'Hello, $greet',
                    style: AppTextStyles.titleMedium().copyWith(fontSize: 22, fontWeight: FontWeight.w600),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'If you need help, use the button below. Responders use your profile to reach you safely.',
                    style: AppTextStyles.heroSupporting(),
                    maxLines: 5,
                    overflow: TextOverflow.fade,
                    softWrap: true,
                  ),
                ],
              );
            },
            loading: () => Text('Loading…', style: AppTextStyles.bodyMuted(), maxLines: 1),
            error: (_, __) => Text(
              'Welcome back',
              style: AppTextStyles.titleMedium().copyWith(fontSize: 20),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const SizedBox(height: 24),
          AppButton(
            label: 'Request help',
            hero: true,
            onPressed: () => context.push(AppRoutes.requestHelp),
          ),
          const SizedBox(height: 14),
          _VoiceRequestCard(onTap: () {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Voice requests will be available in a future update.'),
                behavior: SnackBarBehavior.floating,
              ),
            );
          }),
          const SizedBox(height: 22),
          lastIdAsync.when(
            data: (lastId) {
              if (lastId == null || lastId.isEmpty) {
                return const SizedBox.shrink();
              }
              final detailAsync = ref.watch(incidentDetailProvider(lastId));
              return detailAsync.when(
                data: (d) {
                  if (!_incidentStillActive(d.status)) {
                    return _MutedCard(
                      title: 'Recent support',
                      body:
                          'Incident ${d.incidentId} is marked ${d.status}. You can open tracking for the full timeline.',
                      actionLabel: 'View timeline',
                      onAction: () => context.push(AppRoutes.incidentDetail(d.incidentId)),
                    );
                  }
                  return _ActiveIncidentCard(
                    incidentId: d.incidentId,
                    status: d.status,
                    priority: d.priorityLabel,
                    summary: d.note.isNotEmpty ? d.note : d.incidentType,
                    onOpenTracking: () => context.push(AppRoutes.incidentDetail(d.incidentId)),
                  );
                },
                loading: () => const Padding(
                  padding: EdgeInsets.symmetric(vertical: 12),
                  child: Center(child: CircularProgressIndicator()),
                ),
                error: (_, __) => const SizedBox.shrink(),
              );
            },
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
          ),
          const SizedBox(height: 20),
          Text(
            'Trusted support',
            style: AppTextStyles.titleMedium().copyWith(fontSize: 16),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 10),
          _ShortcutTile(
            icon: Icons.health_and_safety_outlined,
            title: 'Support directory',
            subtitle: 'Shelters, hospitals, and community contacts',
            onTap: () => context.push(AppRoutes.supportDirectory),
          ),
          const SizedBox(height: 8),
          _ShortcutTile(
            icon: Icons.person_outline,
            title: 'Your profile',
            subtitle: 'Emergency details responders may rely on',
            onTap: () => context.push(AppRoutes.profile),
          ),
        ],
        ),
      ),
    );
  }
}

class _VoiceRequestCard extends StatelessWidget {
  const _VoiceRequestCard({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: AppColors.surfaceCard,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.borderSubtle),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.iconSoftFill.withValues(alpha: 0.35),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.mic_none_rounded, color: AppColors.primary),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Voice request',
                      style: AppTextStyles.titleMedium().copyWith(fontSize: 16),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Start a hands-free help request when you cannot type.',
                      style: AppTextStyles.bodyMuted(),
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: AppColors.textTertiary),
            ],
          ),
        ),
      ),
    );
  }
}

class _ActiveIncidentCard extends StatelessWidget {
  const _ActiveIncidentCard({
    required this.incidentId,
    required this.status,
    required this.priority,
    required this.summary,
    required this.onOpenTracking,
  });

  final String incidentId;
  final String status;
  final String priority;
  final String summary;
  final VoidCallback onOpenTracking;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.primary.withValues(alpha: 0.25)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.support_agent, size: 22, color: AppColors.primary),
              const SizedBox(width: 8),
              Text('Active support', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            '$priority · $status',
            style: AppTextStyles.bodyMuted(),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 8),
          Text(summary, maxLines: 3, overflow: TextOverflow.ellipsis, style: AppTextStyles.body()),
          const SizedBox(height: 14),
          Align(
            alignment: Alignment.centerLeft,
            child: TextButton.icon(
              onPressed: onOpenTracking,
              icon: const Icon(Icons.map_outlined, size: 20),
              label: const Text('Track this incident'),
            ),
          ),
        ],
      ),
    );
  }
}

class _MutedCard extends StatelessWidget {
  const _MutedCard({
    required this.title,
    required this.body,
    required this.actionLabel,
    required this.onAction,
  });

  final String title;
  final String body;
  final String actionLabel;
  final VoidCallback onAction;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: AppTextStyles.titleMedium().copyWith(fontSize: 15),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 8),
          Text(
            body,
            style: AppTextStyles.bodyMuted(),
            maxLines: 5,
            overflow: TextOverflow.ellipsis,
          ),
          TextButton(onPressed: onAction, child: Text(actionLabel)),
        ],
      ),
    );
  }
}

class _ShortcutTile extends StatelessWidget {
  const _ShortcutTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: AppColors.surfaceCard,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          child: Row(
            children: [
              Icon(icon, color: AppColors.primary),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: AppTextStyles.body().copyWith(fontWeight: FontWeight.w600),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    Text(
                      subtitle,
                      style: AppTextStyles.microcopy(),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: AppColors.textTertiary, size: 22),
            ],
          ),
        ),
      ),
    );
  }
}
