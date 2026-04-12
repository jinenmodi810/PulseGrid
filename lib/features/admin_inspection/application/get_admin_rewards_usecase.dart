import '../../../core/utils/result.dart';
import '../data/admin_inspection_dtos.dart';
import '../data/admin_inspection_repository.dart';

class GetAdminRewardsUsecase {
  GetAdminRewardsUsecase(this._repository);

  final AdminInspectionRepository _repository;

  Future<Result<List<AdminRewardDto>, String>> call() => _repository.getRewards();
}
