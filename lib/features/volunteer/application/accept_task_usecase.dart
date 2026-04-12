import '../../../core/utils/result.dart';
import '../data/volunteer_task_item_dto.dart';
import '../data/volunteer_tasks_repository.dart';

class AcceptTaskUsecase {
  AcceptTaskUsecase(this._repository);

  final VolunteerTasksRepository _repository;

  Future<Result<AcceptTaskResultDto, String>> call({
    required String incidentId,
    required String volunteerId,
  }) {
    return _repository.acceptTask(incidentId: incidentId, volunteerId: volunteerId);
  }
}
