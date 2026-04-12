import 'package:flutter/material.dart';

import '../../../../app/theme/app_colors.dart';

/// Subtle layered cards + pulse motif — Flutter only, minimal decoration.
class LandingPulseHeroArt extends StatelessWidget {
  const LandingPulseHeroArt({super.key});

  @override
  Widget build(BuildContext context) {
    return const SizedBox(
      height: 156,
      width: double.infinity,
      child: CustomPaint(painter: _LandingHeroPainter()),
    );
  }
}

class _LandingHeroPainter extends CustomPainter {
  const _LandingHeroPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width * 0.5, size.height * 0.48);
    const cardW = 118.0;
    const cardH = 76.0;
    const radius = Radius.circular(14);

    final fill = Paint()..color = AppColors.surfaceCard;
    final stroke = Paint()
      ..color = AppColors.border
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    // Rear card (soft depth)
    final back = RRect.fromRectAndRadius(
      Rect.fromCenter(center: center.translate(14, 10), width: cardW, height: cardH),
      radius,
    );
    canvas.drawRRect(back, fill);
    canvas.drawRRect(back, stroke);

    // Front card
    final front = RRect.fromRectAndRadius(
      Rect.fromCenter(center: center.translate(-10, -8), width: cardW, height: cardH),
      radius,
    );
    canvas.drawRRect(front, fill);
    canvas.drawRRect(front, stroke);

    // Pulse rings (calm, low contrast)
    final ring = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1
      ..color = AppColors.primary.withValues(alpha: 0.12);
    for (var i = 1; i <= 4; i++) {
      canvas.drawCircle(center.translate(-4, -4), 18.0 + i * 13, ring);
    }

    // Soft “signal” stroke across front card
    final pulse = Paint()
      ..color = AppColors.primary.withValues(alpha: 0.35)
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(
      Offset(center.dx - 42, center.dy - 8),
      Offset(center.dx + 28, center.dy - 8),
      pulse,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
