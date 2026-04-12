import '../../../core/utils/result.dart';
import '../data/admin_inspection_dtos.dart';
import '../data/admin_inspection_repository.dart';

class GetAdminIncidentsUsecase {
  GetAdminIncidentsUsecase(this._repository);

  final AdminInspectionRepository _repository;

  Future<Result<List<AdminIncidentDto>, String>> call() => _repository.getIncidents();
}
