import '../../../core/utils/result.dart';
import '../data/auth_repository.dart';
import '../data/session_store.dart';
import '../domain/register_user_payload.dart';

class RegisterAffectedUserUsecase {
  RegisterAffectedUserUsecase(this._repository, this._sessionStore);

  final AuthRepository _repository;
  final SessionStore _sessionStore;

  Future<Result<void, String>> call(RegisterUserPayload payload) async {
    final result = await _repository.registerVictim(payload);
    switch (result) {
      case Success(:final data):
        await _sessionStore.saveAffectedUser(
          userId: data.id,
          zoneId: payload.homeZoneId,
          accessToken: data.accessToken,
          householdSize: payload.householdSize,
          elderlyCount: payload.elderlyCount,
          oxygenDependency: payload.oxygenDependency,
          preferredLanguage: payload.preferredLanguage,
          mobilityConcern: payload.mobilityConcern,
        );
        return const Success<void, String>(null);
      case Failure(:final error):
        return Failure<void, String>(error);
    }
  }
}
