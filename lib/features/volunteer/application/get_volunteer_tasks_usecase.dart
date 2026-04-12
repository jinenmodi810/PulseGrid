import '../../../core/utils/result.dart';
import '../data/volunteer_task_item_dto.dart';
import '../data/volunteer_tasks_repository.dart';

class GetVolunteerTasksUsecase {
  GetVolunteerTasksUsecase(this._repository);

  final VolunteerTasksRepository _repository;

  Future<Result<List<VolunteerTaskItemDto>, String>> call(String volunteerId) {
    return _repository.getTasks(volunteerId);
  }
}
