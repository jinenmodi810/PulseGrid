import 'package:flutter_test/flutter_test.dart';
import 'package:pulsegrid/core/utils/result.dart';

void main() {
  test('Result.fold routes success and failure', () {
    const ok = Success<int, String>(7);
    expect(ok.fold(onSuccess: (v) => v, onFailure: (_) => -1), 7);

    const bad = Failure<int, String>('nope');
    expect(bad.fold(onSuccess: (v) => v, onFailure: (e) => e), 'nope');
  });
}
