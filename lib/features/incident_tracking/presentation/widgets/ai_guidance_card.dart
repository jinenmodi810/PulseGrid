import 'package:flutter/material.dart';

import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';

/// Calm, non-chat operational guidance (copy from backend / Gemini).
class AiGuidanceCard extends StatelessWidget {
  const AiGuidanceCard({
    super.key,
    required this.message,
    this.title = 'Guidance',
    this.loading = false,
    this.isError = false,
    this.fallbackUsed = false,
    this.languageCode,
    this.onRefresh,
  });

  final String message;
  final String title;
  final bool loading;
  final bool isError;
  final bool fallbackUsed;
  final String? languageCode;
  final VoidCallback? onRefresh;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Text(title, style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
              ),
              if (onRefresh != null)
                IconButton(
                  tooltip: 'Refresh guidance',
                  icon: const Icon(Icons.refresh, size: 22),
                  onPressed: loading ? null : onRefresh,
                ),
            ],
          ),
          if (languageCode != null && languageCode!.isNotEmpty && languageCode != 'en') ...[
            const SizedBox(height: 4),
            Text(
              'Guidance adapted where possible to your preferred language ($languageCode).',
              style: AppTextStyles.microcopy().copyWith(color: AppColors.textTertiary),
            ),
          ],
          const SizedBox(height: 8),
          if (loading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 12),
              child: Center(child: SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2))),
            )
          else
            Text(
              isError
                  ? message
                  : (message.isEmpty
                      ? 'Guidance will load from the server when available.'
                      : message),
              style: AppTextStyles.body().copyWith(
                color: isError ? AppColors.danger : AppColors.textPrimary,
                height: 1.35,
              ),
            ),
          if (!loading && fallbackUsed) ...[
            const SizedBox(height: 10),
            Text(
              'Showing a built-in template because the AI service was unavailable.',
              style: AppTextStyles.microcopy().copyWith(color: AppColors.textSecondary),
            ),
          ],
        ],
      ),
    );
  }
}
