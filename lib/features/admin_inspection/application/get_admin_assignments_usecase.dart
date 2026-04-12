import '../../../core/utils/result.dart';
import '../data/admin_inspection_dtos.dart';
import '../data/admin_inspection_repository.dart';

class GetAdminAssignmentsUsecase {
  GetAdminAssignmentsUsecase(this._repository);

  final AdminInspectionRepository _repository;

  Future<Result<List<AdminAssignmentDto>, String>> call() => _repository.getAssignments();
}
