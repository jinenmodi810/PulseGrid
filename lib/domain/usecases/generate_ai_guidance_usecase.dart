import '../../core/services/gemini_service.dart';
import '../../data/models/ai_guidance_model.dart';

class GenerateAiGuidanceUseCase {
  GenerateAiGuidanceUseCase(this._geminiService);

  final GeminiService _geminiService;

  // TODO(Phase1): call GeminiService once API wiring exists.
  Future<AiGuidanceModel> call({required String incidentId}) async {
    return AiGuidanceModel(
      title: 'Operational checklist',
      body: 'Placeholder guidance for $incidentId. Gemini key present: ${_geminiService.apiKey != null && _geminiService.apiKey!.isNotEmpty}.',
      generatedAt: DateTime.now(),
    );
  }
}
