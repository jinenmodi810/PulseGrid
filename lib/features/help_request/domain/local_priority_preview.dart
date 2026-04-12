import 'dart:math' as math;

import 'priority_preview_payload.dart';

/// Instant priority preview aligned with [backend/app/services/priority_service.py].
class LocalPriorityPreview {
  const LocalPriorityPreview({required this.score, required this.label});

  final double score;
  final String label;

  static LocalPriorityPreview fromDraft({
    required String severity,
    required int peopleCount,
    required bool elderly,
    required bool childPresent,
    required bool injury,
    required bool oxygenRequired,
    required bool shelterNeeded,
    required bool foodNeeded,
    required bool transportNeeded,
  }) {
    return compute(
      PriorityPreviewPayload(
        severity: severity,
        peopleCount: peopleCount,
        elderly: elderly,
        childPresent: childPresent,
        injury: injury,
        oxygenRequired: oxygenRequired,
        shelterNeeded: shelterNeeded,
        foodNeeded: foodNeeded,
        transportNeeded: transportNeeded,
      ),
    );
  }

  static LocalPriorityPreview compute(PriorityPreviewPayload p) {
    final sev = p.severity.toLowerCase();
    const base = {'low': 12.0, 'medium': 28.0, 'high': 48.0, 'critical': 68.0};
    var score = base[sev] ?? 28.0;
    if (p.elderly) score += 10.0;
    if (p.childPresent) score += 8.0;
    if (p.injury) score += 12.0;
    if (p.oxygenRequired) score += 14.0;
    if (p.shelterNeeded) score += 6.0;
    if (p.foodNeeded) score += 4.0;
    if (p.transportNeeded) score += 5.0;
    if (p.peopleCount > 1) {
      score += math.min(12.0, (p.peopleCount - 1) * 3.0);
    }
    score = math.min(100.0, (score * 100).round() / 100);

    final label = score >= 82.0
        ? 'CRITICAL'
        : score >= 58.0
            ? 'HIGH'
            : score >= 32.0
                ? 'MEDIUM'
                : 'LOW';

    return LocalPriorityPreview(score: score, label: label);
  }
}
