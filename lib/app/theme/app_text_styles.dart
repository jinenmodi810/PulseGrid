import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'app_colors.dart';

/// Typography scale built on Google Fonts (Inter).
class AppTextStyles {
  const AppTextStyles._();

  static TextStyle get _base => GoogleFonts.inter(color: AppColors.textPrimary);

  /// Premium onboarding hero title.
  static TextStyle heroDisplay() => GoogleFonts.inter(
        fontSize: 34,
        fontWeight: FontWeight.w700,
        height: 1.12,
        letterSpacing: -0.6,
        color: AppColors.textPrimary,
      );

  /// Tagline under app name.
  static TextStyle heroTagline() => GoogleFonts.inter(
        fontSize: 17,
        fontWeight: FontWeight.w500,
        height: 1.35,
        color: AppColors.textSecondary,
      );

  /// Supporting copy under tagline.
  static TextStyle heroSupporting() => GoogleFonts.inter(
        fontSize: 15,
        fontWeight: FontWeight.w400,
        height: 1.45,
        color: AppColors.textSecondary,
      );

  /// Small uppercase labels (badges, eyebrow).
  static TextStyle eyebrow() => GoogleFonts.inter(
        fontSize: 11,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.8,
        color: AppColors.textTertiary,
      );

  static TextStyle titleLarge() => _base.copyWith(fontSize: 22, fontWeight: FontWeight.w700);

  static TextStyle titleMedium() => _base.copyWith(fontSize: 18, fontWeight: FontWeight.w600);

  static TextStyle body() => _base.copyWith(fontSize: 15, fontWeight: FontWeight.w400);

  static TextStyle bodyMuted() =>
      _base.copyWith(fontSize: 14, fontWeight: FontWeight.w400, color: AppColors.textSecondary);

  static TextStyle label() =>
      _base.copyWith(fontSize: 12, fontWeight: FontWeight.w600, letterSpacing: 0.2);

  /// Value card title.
  static TextStyle valueCardTitle() =>
      _base.copyWith(fontSize: 16, fontWeight: FontWeight.w600, height: 1.25);

  /// Value card subtitle.
  static TextStyle valueCardSubtitle() => GoogleFonts.inter(
        fontSize: 13,
        fontWeight: FontWeight.w400,
        height: 1.35,
        color: AppColors.textSecondary,
      );

  /// Trust strip line.
  static TextStyle trustStrip() => GoogleFonts.inter(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: AppColors.textSecondary,
      );

  /// Footer microcopy.
  static TextStyle microcopy() => GoogleFonts.inter(
        fontSize: 12,
        fontWeight: FontWeight.w400,
        height: 1.35,
        color: AppColors.textTertiary,
      );
}
