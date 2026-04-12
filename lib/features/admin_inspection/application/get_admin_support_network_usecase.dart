import '../../../core/utils/result.dart';
import '../data/admin_inspection_dtos.dart';
import '../data/admin_inspection_repository.dart';

class GetAdminSupportNetworkUsecase {
  GetAdminSupportNetworkUsecase(this._repository);

  final AdminInspectionRepository _repository;

  Future<Result<AdminSupportNetworkDto, String>> call() => _repository.getSupportNetwork();
}
