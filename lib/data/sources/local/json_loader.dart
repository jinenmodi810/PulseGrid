import 'package:flutter/services.dart';

/// Loads JSON and other text assets from the Flutter asset bundle.
class JsonLoader {
  JsonLoader(this._bundle);

  final AssetBundle _bundle;

  Future<String> loadString(String assetPath) => _bundle.loadString(assetPath);
}
