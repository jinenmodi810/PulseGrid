import '../../../core/utils/result.dart';
import '../data/admin_inspection_dtos.dart';
import '../data/admin_inspection_repository.dart';

class GetAdminIncidentDetailUsecase {
  GetAdminIncidentDetailUsecase(this._repository);

  final AdminInspectionRepository _repository;

  Future<Result<AdminIncidentDetailDto, String>> call(String incidentId) {
    return _repository.getIncidentDetail(incidentId);
  }
}
