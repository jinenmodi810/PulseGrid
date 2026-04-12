import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/services/gemini_service.dart';
import '../core/services/mock_data_service.dart';
import '../core/services/notification_service.dart';
import '../core/services/storage_service.dart';
import '../core/utils/result.dart';
import '../data/repositories/hospital_repository.dart';
import '../data/repositories/incident_repository.dart';
import '../data/repositories/responder_repository.dart';
import '../data/repositories/rewards_repository.dart';
import '../data/repositories/routing_repository.dart';
import '../data/repositories/shelter_repository.dart';
import '../data/repositories/support_repository.dart';
import '../data/repositories/volunteer_repository.dart';
import '../data/sources/local/json_loader.dart';
import '../features/auth/data/session_store.dart';
import '../data/sources/remote/api_client.dart';
import '../domain/usecases/assign_destination_usecase.dart';
import '../domain/usecases/calculate_priority_usecase.dart';
import '../domain/usecases/compute_route_usecase.dart';
import '../domain/usecases/generate_ai_guidance_usecase.dart';
import '../domain/usecases/get_support_contacts_usecase.dart';
import '../domain/usecases/match_best_helper_usecase.dart';
import '../domain/usecases/update_volunteer_credits_usecase.dart';

final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnsupportedError('sharedPreferencesProvider must be overridden in ProviderScope (see main.dart).');
});

final jsonLoaderProvider = Provider<JsonLoader>((ref) => JsonLoader(rootBundle));

final mockDataServiceProvider = Provider<MockDataService>((ref) {
  return MockDataService(ref.watch(jsonLoaderProvider));
});

final sessionStoreProvider = Provider<SessionStore>((ref) {
  return SessionStore(ref.watch(storageServiceProvider));
});

final apiClientProvider = Provider<ApiClient>((ref) {
  final client = ApiClient(sessionStore: ref.watch(sessionStoreProvider));
  client.configureBaseUrl();
  return client;
});

final geminiServiceProvider = Provider<GeminiService>((ref) => GeminiService.fromDotEnv());

final notificationServiceProvider = Provider<NotificationService>((ref) => const NotificationService());

final storageServiceProvider = Provider<StorageService>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return SharedPreferencesStorageService(prefs);
});

final incidentRepositoryProvider = Provider<IncidentRepository>((ref) {
  return IncidentRepository(ref.watch(mockDataServiceProvider));
});

final volunteerRepositoryProvider = Provider<VolunteerRepository>((ref) {
  return VolunteerRepository(ref.watch(mockDataServiceProvider));
});

final responderRepositoryProvider = Provider<ResponderRepository>((ref) {
  return ResponderRepository(ref.watch(mockDataServiceProvider));
});

final hospitalRepositoryProvider = Provider<HospitalRepository>((ref) {
  return HospitalRepository(ref.watch(mockDataServiceProvider));
});

final shelterRepositoryProvider = Provider<ShelterRepository>((ref) {
  return ShelterRepository(ref.watch(mockDataServiceProvider));
});

final supportRepositoryProvider = Provider<SupportRepository>((ref) {
  return SupportRepository(ref.watch(apiClientProvider));
});

final rewardsRepositoryProvider = Provider<RewardsRepository>((ref) {
  return RewardsRepository(ref.watch(apiClientProvider));
});

final routingRepositoryProvider = Provider<RoutingRepository>((ref) {
  return RoutingRepository(ref.watch(mockDataServiceProvider));
});

final calculatePriorityUseCaseProvider = Provider<CalculatePriorityUseCase>((ref) {
  return const CalculatePriorityUseCase();
});

final matchBestHelperUseCaseProvider = Provider<MatchBestHelperUseCase>((ref) {
  return const MatchBestHelperUseCase();
});

final assignDestinationUseCaseProvider = Provider<AssignDestinationUseCase>((ref) {
  return const AssignDestinationUseCase();
});

final computeRouteUseCaseProvider = Provider<ComputeRouteUseCase>((ref) {
  return const ComputeRouteUseCase();
});

final generateAiGuidanceUseCaseProvider = Provider<GenerateAiGuidanceUseCase>((ref) {
  return GenerateAiGuidanceUseCase(ref.watch(geminiServiceProvider));
});

final updateVolunteerCreditsUseCaseProvider = Provider<UpdateVolunteerCreditsUseCase>((ref) {
  return const UpdateVolunteerCreditsUseCase();
});

final getSupportContactsUsecaseProvider = Provider<GetSupportContactsUsecase>((ref) {
  return GetSupportContactsUsecase(ref.watch(supportRepositoryProvider));
});

final incidentsProvider = FutureProvider((ref) async {
  final repo = ref.watch(incidentRepositoryProvider);
  final result = await repo.getIncidents();
  return switch (result) {
    Success(:final data) => data,
    Failure(:final error) => throw StateError(error),
  };
});

final supportContactsProvider = FutureProvider((ref) async {
  final usecase = ref.watch(getSupportContactsUsecaseProvider);
  final result = await usecase.call();
  return switch (result) {
    Success(:final data) => data,
    Failure(:final error) => throw StateError(error),
  };
});

final rewardsProvider = FutureProvider((ref) async {
  final repo = ref.watch(rewardsRepositoryProvider);
  final result = await repo.getRewards();
  return switch (result) {
    Success(:final data) => data,
    Failure(:final error) => throw StateError(error),
  };
});
