import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/enums/user_role.dart';
import '../../../../app/providers.dart';
import '../../../auth/presentation/providers/auth_providers.dart';
import '../../../auth/presentation/utils/session_navigation.dart';
import '../../../organization/presentation/providers/organization_providers.dart';
import '../../../volunteer/presentation/providers/volunteer_realtime_provider.dart';
import '../../../volunteer/presentation/providers/volunteer_task_providers.dart';
import '../widgets/trust_score_card.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  Future<void> _onBack(BuildContext context, WidgetRef ref) async {
    if (context.canPop()) {
      context.pop();
      return;
    }
    final session = ref.read(sessionStoreProvider);
    final role = await session.readRole();
    if (!context.mounted) {
      return;
    }
    switch (role) {
      case UserRole.affectedUser:
        context.go(AppRoutes.victimHome);
      case UserRole.volunteer:
        context.go(AppRoutes.volunteerHome);
      case UserRole.organization:
        context.go(AppRoutes.organizationDashboard);
      case null:
        context.go(AppRoutes.landing);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = ref.watch(sessionStoreProvider);

    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Your profile'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => _onBack(context, ref),
        ),
      ),
      body: FutureBuilder<UserRole?>(
        future: session.readRole(),
        builder: (context, snap) {
          final role = snap.data;
          if (role == null) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Text('No saved session on this device.', style: AppTextStyles.bodyMuted()),
              ),
            );
          }
          return ListView(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
            children: [
              switch (role) {
                UserRole.affectedUser => const _VictimProfileSection(),
                UserRole.volunteer => const _VolunteerProfileSection(),
                UserRole.organization => const _OrganizationProfileSection(),
              },
              const SizedBox(height: 28),
              OutlinedButton(
                onPressed: () => signOutAndGoLanding(ref, context),
                child: const Text('Sign out'),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _VictimProfileSection extends ConsumerWidget {
  const _VictimProfileSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(victimProfileBySessionProvider);
    return async.when(
      data: (p) {
        if (p == null) {
          return Text('Profile could not be loaded.', style: AppTextStyles.bodyMuted());
        }
        return _ProfileCard(
          children: [
            _kv('Name', p.fullName),
            if (p.email.isNotEmpty) _kv('Email', p.email),
            _kv('Phone', p.phone),
            _kv('Preferred language', p.preferredLanguage),
            _kv('Home zone', p.zoneId),
            _kv('Household', '${p.householdSize} people · ${p.elderlyCount} older adults'),
            _kv('Mobility support', p.mobilityConcern ? 'Yes' : 'No'),
            _kv('Oxygen dependency', p.oxygenDependency ? 'Yes' : 'No'),
            const Divider(height: 28),
            Text('Emergency contact', style: AppTextStyles.titleMedium().copyWith(fontSize: 15)),
            const SizedBox(height: 8),
            _kv('Name', p.emergencyContactName.isEmpty ? '—' : p.emergencyContactName),
            _kv('Phone', p.emergencyContactPhone.isEmpty ? '—' : p.emergencyContactPhone),
            _kv('Relationship', p.emergencyContactRelationship.isEmpty ? '—' : p.emergencyContactRelationship),
          ],
        );
      },
      loading: () => const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator())),
      error: (_, __) => Text('Unable to load profile.', style: AppTextStyles.bodyMuted()),
    );
  }
}

class _VolunteerProfileSection extends ConsumerWidget {
  const _VolunteerProfileSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.watch(volunteerRealtimeBySessionProvider);
    final async = ref.watch(volunteerProfileBySessionProvider);
    return async.when(
      data: (v) {
        if (v == null) {
          return Text('Volunteer profile not found for this session.', style: AppTextStyles.bodyMuted());
        }
        return _ProfileCard(
          children: [
            _kv('Name', v.displayName),
            _kv('Zone', v.zoneId.isEmpty ? '—' : v.zoneId),
            _kv('Skills', v.skills.isEmpty ? '—' : v.skills.join(', ')),
            _kv('Support types', v.supportTypes.isEmpty ? '—' : v.supportTypes.join(', ')),
            _kv('Languages', v.languages.isEmpty ? '—' : v.languages.join(', ')),
            _kv('Transport', v.transportAccess.isEmpty ? '—' : v.transportAccess),
            _kv('Availability', v.availability.isEmpty ? '—' : v.availability),
            const SizedBox(height: 16),
            TrustScoreCard(score: v.trustScore.clamp(0.0, 1.0)),
            const SizedBox(height: 10),
            _kv('Credits', '${v.credits}'),
          ],
        );
      },
      loading: () => const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator())),
      error: (_, __) => Text('Unable to load profile.', style: AppTextStyles.bodyMuted()),
    );
  }
}

class _OrganizationProfileSection extends ConsumerWidget {
  const _OrganizationProfileSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(organizationOverviewProvider);
    return async.when(
      data: (o) {
        return _ProfileCard(
          children: [
            _kv('Organization', o.name),
            _kv('Type', o.orgType.replaceAll('_', ' ')),
            _kv('Zone / coverage', o.zoneId),
            _kv('Status', o.active ? 'Active' : 'Inactive'),
            _kv('Open assigned incidents', '${o.assignedIncidentsOpen}'),
            const Divider(height: 28),
            Text('Capabilities & capacity', style: AppTextStyles.titleMedium().copyWith(fontSize: 15)),
            const SizedBox(height: 8),
            if (o.capacity.isEmpty)
              Text('No capacity fields returned yet.', style: AppTextStyles.bodyMuted())
            else
              ...o.capacity.entries.map((e) => _kv(_capLabel(e.key), '${e.value}')),
          ],
        );
      },
      loading: () => const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator())),
      error: (_, __) => Text('Unable to load organization profile.', style: AppTextStyles.bodyMuted()),
    );
  }
}

String _capLabel(String key) {
  return key.replaceAll('_', ' ');
}

class _ProfileCard extends StatelessWidget {
  const _ProfileCard({required this.children});

  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: children),
    );
  }
}

Widget _kv(String label, String value) {
  return Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppTextStyles.microcopy()),
        const SizedBox(height: 2),
        Text(value, style: AppTextStyles.body()),
      ],
    ),
  );
}
