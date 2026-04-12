import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/providers.dart';
import '../../../../core/utils/result.dart';
import '../../application/login_organization_usecase.dart';
import '../../application/login_victim_usecase.dart';
import '../../application/login_volunteer_usecase.dart';
import '../../application/register_affected_user_usecase.dart';
import '../../application/register_organization_account_usecase.dart';
import '../../application/register_volunteer_account_usecase.dart';
import '../../data/auth_repository.dart';
import '../../data/victim_user_profile_dto.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.watch(apiClientProvider));
});

final registerAffectedUserUsecaseProvider = Provider<RegisterAffectedUserUsecase>((ref) {
  return RegisterAffectedUserUsecase(
    ref.watch(authRepositoryProvider),
    ref.watch(sessionStoreProvider),
  );
});

final registerVolunteerAccountUsecaseProvider = Provider<RegisterVolunteerAccountUsecase>((ref) {
  return RegisterVolunteerAccountUsecase(
    ref.watch(authRepositoryProvider),
    ref.watch(sessionStoreProvider),
  );
});

final registerOrganizationAccountUsecaseProvider = Provider<RegisterOrganizationAccountUsecase>((ref) {
  return RegisterOrganizationAccountUsecase(
    ref.watch(authRepositoryProvider),
    ref.watch(sessionStoreProvider),
  );
});

final loginVictimUsecaseProvider = Provider<LoginVictimUsecase>((ref) {
  return LoginVictimUsecase(ref.watch(authRepositoryProvider), ref.watch(sessionStoreProvider));
});

final loginVolunteerUsecaseProvider = Provider<LoginVolunteerUsecase>((ref) {
  return LoginVolunteerUsecase(ref.watch(authRepositoryProvider), ref.watch(sessionStoreProvider));
});

final loginOrganizationUsecaseProvider = Provider<LoginOrganizationUsecase>((ref) {
  return LoginOrganizationUsecase(ref.watch(authRepositoryProvider), ref.watch(sessionStoreProvider));
});

/// Affected-user profile for the signed-in graph user id, or null if not in that role.
final victimProfileBySessionProvider = FutureProvider<VictimUserProfileDto?>((ref) async {
  final storage = ref.watch(storageServiceProvider);
  final id = await storage.getString(SessionKeys.graphUserId);
  if (id == null || id.isEmpty) {
    return null;
  }
  final repo = ref.watch(authRepositoryProvider);
  final result = await repo.getUserProfile(id);
  return switch (result) {
    Success(:final data) => data,
    Failure() => null,
  };
});

final dashboardSummaryProvider = FutureProvider((ref) async {
  final repo = ref.watch(authRepositoryProvider);
  final result = await repo.dashboardSummary();
  return switch (result) {
    Success(:final data) => data,
    Failure(:final error) => throw StateError(error),
  };
});
