import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'constants/app_constants.dart';
import 'theme/app_colors.dart';
import 'theme/app_text_styles.dart';

/// Shown only for routes that are not part of the supported GoRouter map.
class NotFoundScreen extends StatelessWidget {
  const NotFoundScreen({super.key, required this.attemptedPath});

  final String attemptedPath;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Page not found'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'No route is registered for this path.',
              style: AppTextStyles.titleMedium(),
            ),
            const SizedBox(height: 8),
            Text(
              attemptedPath,
              style: AppTextStyles.bodyMuted(),
            ),
            const SizedBox(height: 28),
            FilledButton(
              onPressed: () => context.go(AppRoutes.landing),
              child: const Text('Back to PulseGrid'),
            ),
          ],
        ),
      ),
    );
  }
}
