import '../../../core/utils/result.dart';
import '../../incident_tracking/data/ai_guidance_repository.dart';

class GetVolunteerGuidanceUsecase {
  GetVolunteerGuidanceUsecase(this._repository);

  final AiGuidanceRepository _repository;

  Future<Result<GuidanceDto, String>> call({
    required String incidentId,
    String? volunteerId,
  }) {
    return _repository.postVolunteerGuidance(incidentId: incidentId, volunteerId: volunteerId);
  }
}
