/// Shared date formatting helpers.
class AppDateUtils {
  const AppDateUtils._();

  static DateTime? tryParseIso(String? raw) {
    if (raw == null || raw.isEmpty) {
      return null;
    }
    return DateTime.tryParse(raw);
  }

  /// Compact local date (no extra packages).
  static String formatShort(DateTime date) {
    final d = date.toLocal();
    final y = d.year.toString().padLeft(4, '0');
    final m = d.month.toString().padLeft(2, '0');
    final day = d.day.toString().padLeft(2, '0');
    return '$y-$m-$day';
  }
}
