import '../../core/utils/result.dart';
import '../../data/models/support_contact_model.dart';
import '../../data/repositories/support_repository.dart';

class GetSupportContactsUsecase {
  GetSupportContactsUsecase(this._repository);

  final SupportRepository _repository;

  Future<Result<List<SupportContactModel>, String>> call() {
    return _repository.getContacts();
  }
}
