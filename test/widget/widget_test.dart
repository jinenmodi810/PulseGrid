import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pulsegrid/app/app.dart';
import 'package:pulsegrid/app/providers.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  testWidgets('PulseGrid renders splash shell', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(prefs),
        ],
        child: const PulseGridApp(),
      ),
    );

    await tester.pumpAndSettle();
    expect(find.textContaining('PulseGrid'), findsWidgets);
  });
}
