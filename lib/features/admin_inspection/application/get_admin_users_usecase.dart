import '../../../core/utils/result.dart';
import '../data/admin_inspection_dtos.dart';
import '../data/admin_inspection_repository.dart';

class GetAdminUsersUsecase {
  GetAdminUsersUsecase(this._repository);

  final AdminInspectionRepository _repository;

  Future<Result<List<AdminUserDto>, String>> call() => _repository.getUsers();
}
