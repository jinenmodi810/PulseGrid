T enumFromName<T extends Enum>(Iterable<T> values, String? raw, T fallback) {
  if (raw == null || raw.isEmpty) {
    return fallback;
  }
  for (final value in values) {
    if (value.name == raw) {
      return value;
    }
  }
  return fallback;
}
