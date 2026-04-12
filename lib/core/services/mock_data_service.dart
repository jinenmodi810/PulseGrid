import 'dart:convert';

import '../../data/sources/local/json_loader.dart';

/// Mock-first asset loading. Keeps JSON parsing out of repositories.
class MockDataService {
  MockDataService(this._jsonLoader);

  final JsonLoader _jsonLoader;

  Future<List<dynamic>> decodeList(String assetPath) async {
    final text = await _jsonLoader.loadString(assetPath);
    final decoded = jsonDecode(text);
    if (decoded is List<dynamic>) {
      return decoded;
    }
    return const [];
  }
}
