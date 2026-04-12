import '../../../core/utils/result.dart';
import '../data/admin_inspection_dtos.dart';
import '../data/admin_inspection_repository.dart';

class GetAdminVolunteersUsecase {
  GetAdminVolunteersUsecase(this._repository);

  final AdminInspectionRepository _repository;

  Future<Result<List<AdminVolunteerDto>, String>> call() => _repository.getVolunteers();
}
