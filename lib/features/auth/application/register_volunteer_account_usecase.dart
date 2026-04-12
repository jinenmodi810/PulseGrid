import '../../../core/utils/result.dart';
import '../data/auth_repository.dart';
import '../data/session_store.dart';
import '../domain/register_volunteer_payload.dart';

class RegisterVolunteerAccountUsecase {
  RegisterVolunteerAccountUsecase(this._repository, this._sessionStore);

  final AuthRepository _repository;
  final SessionStore _sessionStore;

  Future<Result<void, String>> call(RegisterVolunteerPayload payload) async {
    final result = await _repository.registerVolunteer(payload);
    switch (result) {
      case Success(:final data):
        await _sessionStore.saveVolunteer(
          volunteerId: data.id,
          zoneId: payload.zoneId,
          accessToken: data.accessToken,
          availability: payload.availability,
        );
        return const Success<void, String>(null);
      case Failure(:final error):
        return Failure<void, String>(error);
    }
  }
}
