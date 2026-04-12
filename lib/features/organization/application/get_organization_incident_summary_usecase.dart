import '../../../core/utils/result.dart';
import '../../incident_tracking/data/ai_guidance_repository.dart';

class GetOrganizationIncidentSummaryUsecase {
  GetOrganizationIncidentSummaryUsecase(this._repository);

  final AiGuidanceRepository _repository;

  Future<Result<GuidanceDto, String>> call(String incidentId) async {
    return _repository.postCoordinatorSummary(incidentId: incidentId);
  }
}
