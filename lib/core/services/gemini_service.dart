import 'package:flutter_dotenv/flutter_dotenv.dart';

import '../../app/constants/api_constants.dart';

/// Gemini access should move behind your backend in production.
class GeminiService {
  GeminiService({this.apiKey});

  final String? apiKey;

  factory GeminiService.fromDotEnv() {
    return GeminiService(apiKey: dotenv.maybeGet(ApiConstants.envGeminiApiKey));
  }

  // TODO(Phase1): implement generateGuidance(...) calling Vertex or a backend proxy.
}
