import '../../../core/utils/result.dart';
import '../data/volunteer_task_item_dto.dart';
import '../data/volunteer_tasks_repository.dart';

class CompleteTaskUsecase {
  CompleteTaskUsecase(this._repository);

  final VolunteerTasksRepository _repository;

  Future<Result<CompleteTaskResultDto, String>> call({
    required String incidentId,
    required String volunteerId,
  }) {
    return _repository.completeTask(incidentId: incidentId, volunteerId: volunteerId);
  }
}
