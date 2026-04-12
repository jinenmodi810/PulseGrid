import '../../../core/utils/result.dart';
import '../../incident_tracking/data/incident_detail_dto.dart';
import '../data/help_request_repository.dart';

class GetIncidentTrackingUsecase {
  GetIncidentTrackingUsecase(this._repository);

  final HelpRequestRepository _repository;

  Future<Result<IncidentDetailDto, String>> call(String incidentId) {
    return _repository.getIncident(incidentId);
  }
}
