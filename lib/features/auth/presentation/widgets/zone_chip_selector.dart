import 'package:flutter/material.dart';

import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../constants/zone_options.dart';

/// Single-select zone picker — chip row, mobile-first.
/// TODO: optional map view or multi-zone coverage.
class ZoneChipSelector extends StatelessWidget {
  const ZoneChipSelector({
    super.key,
    required this.selectedZoneId,
    required this.onSelected,
    this.label = 'Home zone',
    this.footnote,
  });

  final String selectedZoneId;
  final ValueChanged<String> onSelected;
  final String label;
  /// Optional helper text (e.g. zone vs live GPS — MVP honesty).
  final String? footnote;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppTextStyles.titleMedium().copyWith(fontSize: 14)),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final id in kAuthZoneIds)
              FilterChip(
                label: Text(zoneLabel(id)),
                selected: id == selectedZoneId,
                onSelected: (selected) {
                  if (selected) onSelected(id);
                },
                showCheckmark: true,
                selectedColor: AppColors.iconSoftFill,
                checkmarkColor: AppColors.primary,
                labelStyle: AppTextStyles.body().copyWith(
                  color: id == selectedZoneId ? AppColors.primary : AppColors.textPrimary,
                  fontWeight: id == selectedZoneId ? FontWeight.w600 : FontWeight.w500,
                ),
                side: BorderSide(
                  color: id == selectedZoneId ? AppColors.primary : AppColors.border,
                ),
              ),
          ],
        ),
        if (footnote != null && footnote!.trim().isNotEmpty) ...[
          const SizedBox(height: 10),
          Text(
            footnote!,
            style: AppTextStyles.bodyMuted().copyWith(fontSize: 12, height: 1.35),
          ),
        ],
      ],
    );
  }
}
