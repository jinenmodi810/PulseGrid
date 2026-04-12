import '../../../core/utils/result.dart';
import '../data/auth_repository.dart';
import '../data/session_store.dart';
class LoginVictimUsecase {
  LoginVictimUsecase(this._repository, this._sessionStore);

  final AuthRepository _repository;
  final SessionStore _sessionStore;

  Future<Result<void, String>> call({required String email, required String password}) async {
    final result = await _repository.loginVictim(email: email, password: password);
    switch (result) {
      case Success(:final data):
        final signIn = data;
        await _sessionStore.saveAffectedUser(
          userId: signIn.id,
          zoneId: '',
          accessToken: signIn.accessToken,
        );
        final me = await _repository.authMe();
        switch (me) {
          case Success(:final data):
            final m = data;
            await _sessionStore.saveAffectedUser(
              userId: m.id,
              zoneId: m.zoneId ?? '',
              accessToken: signIn.accessToken,
              householdSize: m.householdSize,
              elderlyCount: m.elderlyCount,
              oxygenDependency: m.oxygenDependency,
              preferredLanguage: m.preferredLanguage,
              mobilityConcern: m.mobilityConcern,
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
