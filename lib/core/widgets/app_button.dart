import 'package:flutter/material.dart';

enum AppButtonVariant { filled, outlined }

class AppButton extends StatelessWidget {
  const AppButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.variant = AppButtonVariant.filled,
    this.icon,
    /// Taller, full-width primary CTA (e.g. onboarding).
    this.hero = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final AppButtonVariant variant;
  final IconData? icon;
  final bool hero;

  @override
  Widget build(BuildContext context) {
    final fontSize = hero ? 16.0 : 15.0;
    final vertical = hero ? 16.0 : 14.0;
    final minSize = hero ? const Size(double.infinity, 54) : null;

    final child = icon == null
        ? Text(label)
        : Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: hero ? 20 : 18),
              const SizedBox(width: 8),
              Text(label),
            ],
          );

    return switch (variant) {
      AppButtonVariant.filled => FilledButton(
          onPressed: onPressed,
          style: FilledButton.styleFrom(
            minimumSize: minSize,
            textStyle: Theme.of(context).textTheme.labelLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                  fontSize: fontSize,
                ),
            padding: EdgeInsets.symmetric(horizontal: hero ? 24 : 18, vertical: vertical),
          ),
          child: child,
        ),
      AppButtonVariant.outlined => OutlinedButton(
          onPressed: onPressed,
          style: OutlinedButton.styleFrom(
            minimumSize: minSize,
            textStyle: Theme.of(context).textTheme.labelLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                  fontSize: fontSize,
                ),
            padding: EdgeInsets.symmetric(horizontal: hero ? 24 : 18, vertical: vertical),
          ),
          child: child,
        ),
    };
  }
}
