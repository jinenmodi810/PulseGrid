import '../../../core/utils/result.dart';
import '../data/help_request_repository.dart';
import '../domain/priority_preview_payload.dart';

class PreviewHelpPriorityUsecase {
  PreviewHelpPriorityUsecase(this._repository);

  final HelpRequestRepository _repository;

  Future<Result<PriorityPreviewResult, String>> call(PriorityPreviewPayload payload) {
    return _repository.previewPriority(payload);
  }
}
