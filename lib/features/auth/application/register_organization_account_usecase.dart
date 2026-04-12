import '../../../core/utils/result.dart';
import '../data/auth_repository.dart';
import '../data/session_store.dart';
import '../domain/register_organization_payload.dart';

class RegisterOrganizationAccountUsecase {
  RegisterOrganizationAccountUsecase(this._repository, this._sessionStore);

  final AuthRepository _repository;
  final SessionStore _sessionStore;

  Future<Result<void, String>> call(RegisterOrganizationPayload payload) async {
    final result = await _repository.registerOrganization(payload);
    switch (result) {
      case Success(:final data):
        await _sessionStore.saveOrganization(
          organizationId: data.id,
          zoneId: payload.zoneId,
          accessToken: data.accessToken,
          organizationType: payload.organizationType,
        );
        return const Success<void, String>(null);
      case Failure(:final error):
        return Failure<void, String>(error);
    }
  }
}
