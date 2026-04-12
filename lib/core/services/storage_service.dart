import 'package:shared_preferences/shared_preferences.dart';

/// Local key-value persistence. SharedPreferences today; Hive can swap in later.
abstract class StorageService {
  Future<void> setString(String key, String value);
  Future<String?> getString(String key);
  Future<void> remove(String key);
}

class SharedPreferencesStorageService implements StorageService {
  SharedPreferencesStorageService(this._prefs);

  final SharedPreferences _prefs;

  @override
  Future<void> setString(String key, String value) async {
    await _prefs.setString(key, value);
  }

  @override
  Future<String?> getString(String key) async => _prefs.getString(key);

  @override
  Future<void> remove(String key) async {
    await _prefs.remove(key);
  }
}
