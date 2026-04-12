import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/constants/labels.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_button.dart';
import '../widgets/landing_learn_more_sheet.dart';
import '../widgets/landing_pulse_hero_art.dart';
import '../widgets/landing_trust_strip.dart';
import '../widgets/landing_value_card.dart';

/// Premium first entry — calm, trustworthy, mobile-first.
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _fade;
  late final Animation<Offset> _slide;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 780));
    _fade = CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic);
    _slide = Tween<Offset>(begin: const Offset(0, 0.04), end: Offset.zero).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic),
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final horizontal = MediaQuery.sizeOf(context).width >= 390 ? 26.0 : 22.0;

    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      body: SafeArea(
        child: FadeTransition(
          opacity: _fade,
          child: SlideTransition(
            position: _slide,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Expanded(
                  child: SingleChildScrollView(
                    physics: const BouncingScrollPhysics(),
                    padding: EdgeInsets.fromLTRB(horizontal, 12, horizontal, 16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: const [
                            _EyebrowPill(text: Labels.badgeRealtime),
                            _EyebrowPill(text: Labels.badgeTrusted),
                          ],
                        ),
                        const SizedBox(height: 28),
                        Text(
                          AppConstants.appName,
                          style: AppTextStyles.heroDisplay(),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 10),
                        Text(
                          Labels.appTagline,
                          style: AppTextStyles.heroTagline(),
                          maxLines: 3,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          Labels.landingSupporting,
                          style: AppTextStyles.heroSupporting(),
                          maxLines: 8,
                          overflow: TextOverflow.fade,
                          softWrap: true,
                        ),
                        const SizedBox(height: 28),
                        const LandingPulseHeroArt(),
                        const SizedBox(height: 28),
                        const LandingValueCard(
                          icon: Icons.sos_outlined,
                          title: Labels.valueRequestTitle,
                          subtitle: Labels.valueRequestSubtitle,
                        ),
                        const SizedBox(height: 10),
                        const LandingValueCard(
                          icon: Icons.favorite_outline,
                          title: Labels.valueOfferTitle,
                          subtitle: Labels.valueOfferSubtitle,
                        ),
                        const SizedBox(height: 10),
                        const LandingValueCard(
                          icon: Icons.verified_user_outlined,
                          title: Labels.valueSupportTitle,
                          subtitle: Labels.valueSupportSubtitle,
                        ),
                        const SizedBox(height: 22),
                        const LandingTrustStrip(
                          items: [
                            (icon: Icons.shield_outlined, label: Labels.trustResponders),
                            (icon: Icons.groups_2_outlined, label: Labels.trustVolunteers),
                            (icon: Icons.local_hospital_outlined, label: Labels.trustShelters),
                          ],
                        ),
                        const SizedBox(height: 24),
                      ],
                    ),
                  ),
                ),
                Padding(
                  padding: EdgeInsets.fromLTRB(
                    horizontal,
                    0,
                    horizontal,
                    12 + MediaQuery.paddingOf(context).bottom,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      AppButton(
                        label: Labels.continueLabel,
                        hero: true,
                        onPressed: () => context.go(AppRoutes.roleSelect),
                      ),
                      const SizedBox(height: 10),
                      Center(
                        child: TextButton(
                          onPressed: () => showLandingLearnMoreSheet(context),
                          child: Text(
                            Labels.learnMore,
                            style: AppTextStyles.body().copyWith(
                              fontWeight: FontWeight.w600,
                              color: AppColors.primary,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        Labels.landingFooter,
                        textAlign: TextAlign.center,
                        style: AppTextStyles.microcopy(),
                        maxLines: 4,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _EyebrowPill extends StatelessWidget {
  const _EyebrowPill({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Text(text, style: AppTextStyles.eyebrow()),
    );
  }
}
