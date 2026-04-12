import '../../../app/constants/app_constants.dart';
import '../../../core/services/storage_service.dart';
import '../../../core/utils/result.dart';
import '../data/help_request_repository.dart';
import '../domain/help_request_submit_payload.dart';

class SubmitHelpRequestUsecase {
  SubmitHelpRequestUsecase(this._repository, this._storage);

  final HelpRequestRepository _repository;
  final StorageService _storage;

  Future<Result<CreateIncidentResult, String>> call(HelpRequestSubmitPayload payload) async {
    final userId = await _storage.getString(SessionKeys.graphUserId);
    if (userId == null || userId.isEmpty) {
      return const Failure('Please complete registration as an affected user before requesting help.');
    }
    final withUser = HelpRequestSubmitPayload(
      userId: userId,
      incidentType: payload.incidentType,
      severity: payload.severity,
      peopleCount: payload.peopleCount,
      zoneId: payload.zoneId,
      elderly: payload.elderly,
      childPresent: payload.childPresent,
      injury: payload.injury,
      oxygenRequired: payload.oxygenRequired,
      shelterNeeded: payload.shelterNeeded,
      foodNeeded: payload.foodNeeded,
      transportNeeded: payload.transportNeeded,
      note: payload.note,
      useProfileForPeopleCount: payload.useProfileForPeopleCount,
      useProfileForElderly: payload.useProfileForElderly,
      useProfileForOxygenRequired: payload.useProfileForOxygenRequired,
      intakeSource: payload.intakeSource,
    );
    final result = await _repository.createIncident(withUser);
    switch (result) {
      case Success(:final data):
        await _storage.setString(SessionKeys.lastIncidentId, data.incidentId);
        return Success(data);
      case Failure(:final error):
        return Failure(error);
    }
  }
}
