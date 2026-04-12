import '../../../core/utils/result.dart';
import '../data/admin_inspection_dtos.dart';
import '../data/admin_inspection_repository.dart';

class GetAdminOverviewUsecase {
  GetAdminOverviewUsecase(this._repository);

  final AdminInspectionRepository _repository;

  Future<Result<AdminOverviewDto, String>> call() => _repository.getOverview();
}
