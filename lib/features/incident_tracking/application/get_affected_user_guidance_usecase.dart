import '../../../core/utils/result.dart';
import '../data/ai_guidance_repository.dart';

class GetAffectedUserGuidanceUsecase {
  GetAffectedUserGuidanceUsecase(this._repository);

  final AiGuidanceRepository _repository;

  Future<Result<GuidanceDto, String>> call(String incidentId) async {
    final r = await _repository.getIncidentGuidance(incidentId: incidentId, includeCoordinator: false);
    return switch (r) {
      Success(:final data) => Success(data.affectedUser),
      Failure(:final error) => Failure(error),
    };
  }
}
