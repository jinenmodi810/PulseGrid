import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';

/// Branches into the three primary journeys: request support, offer support, organization partner access.
class RoleSelectScreen extends StatelessWidget {
  const RoleSelectScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final pad = MediaQuery.sizeOf(context).width >= 390 ? 26.0 : 22.0;

    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Choose how you want to use PulseGrid'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
          onPressed: () => context.go(AppRoutes.landing),
        ),
      ),
      body: ListView(
        padding: EdgeInsets.fromLTRB(pad, 8, pad, 28),
        children: [
          Text(
            'Each path opens the right tools for you. You can return here anytime from the PulseGrid landing page.',
            style: AppTextStyles.heroSupporting(),
          ),
          const SizedBox(height: 28),
          _RoleCard(
            title: 'Need help',
            subtitle: 'If you are affected, register and tell us what you need. Track your request and see who responds.',
            icon: Icons.sos_outlined,
            onTap: () => context.push(AppRoutes.registerUser),
            secondaryLabel: 'Sign in',
            onSecondary: () => context.push(AppRoutes.loginVictim),
          ),
          const SizedBox(height: 12),
          _RoleCard(
            title: 'Offer help',
            subtitle: 'Volunteer in your area. See open tasks and respond when you can help.',
            icon: Icons.favorite_outline,
            onTap: () => context.push(AppRoutes.registerVolunteer),
            secondaryLabel: 'Sign in',
            onSecondary: () => context.push(AppRoutes.loginVolunteer),
          ),
          const SizedBox(height: 12),
          _RoleCard(
            title: 'Organization / partner access',
            subtitle: 'Hospitals, NGOs, ambulance, rescue, and shelters — manage capacity and assigned incidents.',
            icon: Icons.apartment_outlined,
            onTap: () => context.push(AppRoutes.registerOrganization),
            secondaryLabel: 'Sign in',
            onSecondary: () => context.push(AppRoutes.loginOrganization),
          ),
        ],
      ),
    );
  }
}

class _RoleCard extends StatelessWidget {
  const _RoleCard({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.onTap,
    this.secondaryLabel,
    this.onSecondary,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final VoidCallback onTap;
  final String? secondaryLabel;
  final VoidCallback? onSecondary;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: AppColors.surfaceCard,
      elevation: 0,
      shadowColor: AppColors.textPrimary.withValues(alpha: 0.06),
      borderRadius: BorderRadius.circular(18),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: AppColors.borderSubtle),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            InkWell(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(17)),
              onTap: onTap,
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: AppColors.iconSoftFill,
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Icon(icon, color: AppColors.primary.withValues(alpha: 0.9)),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(title, style: AppTextStyles.valueCardTitle()),
                          const SizedBox(height: 4),
                          Text(subtitle, style: AppTextStyles.valueCardSubtitle()),
                        ],
                      ),
                    ),
                    Icon(Icons.chevron_right_rounded, color: AppColors.textTertiary),
                  ],
                ),
              ),
            ),
            if (secondaryLabel != null && onSecondary != null) ...[
              const Divider(height: 1),
              Padding(
                padding: const EdgeInsets.fromLTRB(8, 0, 8, 4),
                child: TextButton.icon(
                  onPressed: onSecondary,
                  icon: const Icon(Icons.login_rounded, size: 20),
                  label: Text(secondaryLabel!),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
