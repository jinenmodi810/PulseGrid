import '../../../core/utils/result.dart';
import '../data/auth_repository.dart';
import '../data/session_store.dart';
class LoginOrganizationUsecase {
  LoginOrganizationUsecase(this._repository, this._sessionStore);

  final AuthRepository _repository;
  final SessionStore _sessionStore;

  Future<Result<void, String>> call({required String email, required String password}) async {
    final result = await _repository.loginOrganization(email: email, password: password);
    switch (result) {
      case Success(:final data):
        final signIn = data;
        await _sessionStore.saveOrganization(
          organizationId: signIn.id,
          zoneId: '',
          accessToken: signIn.accessToken,
        );
        final me = await _repository.authMe();
        switch (me) {
          case Success(:final data):
            final m = data;
            await _sessionStore.saveOrganization(
              organizationId: m.id,
              zoneId: m.zoneId ?? '',
              accessToken: signIn.accessToken,
              organizationType: m.orgType,
            );
          case Failure():
            break;
        }
        return const Success<void, String>(null);
      case Failure(:final error):
        return Failure<void, String>(error);
    }
  }
}
