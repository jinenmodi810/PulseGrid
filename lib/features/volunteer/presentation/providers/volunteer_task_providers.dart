import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/providers.dart';
import '../../../../core/utils/result.dart';
import '../../../auth/presentation/providers/auth_providers.dart';
import '../../application/accept_task_usecase.dart';
import '../../application/complete_task_usecase.dart';
import '../../application/get_volunteer_tasks_usecase.dart';
import '../../data/volunteer_task_item_dto.dart';
import '../../data/volunteer_tasks_repository.dart';
import '../../../help_request/presentation/providers/help_request_providers.dart';
import '../../../incident_tracking/presentation/providers/ai_guidance_providers.dart';

final volunteerTasksRepositoryProvider = Provider<VolunteerTasksRepository>((ref) {
  return VolunteerTasksRepository(ref.watch(apiClientProvider));
});

final getVolunteerTasksUsecaseProvider = Provider<GetVolunteerTasksUsecase>((ref) {
  return GetVolunteerTasksUsecase(ref.watch(volunteerTasksRepositoryProvider));
});

final acceptTaskUsecaseProvider = Provider<AcceptTaskUsecase>((ref) {
  return AcceptTaskUsecase(ref.watch(volunteerTasksRepositoryProvider));
});

final completeTaskUsecaseProvider = Provider<CompleteTaskUsecase>((ref) {
  return CompleteTaskUsecase(ref.watch(volunteerTasksRepositoryProvider));
});

/// Tasks for the volunteer id stored at [SessionKeys.graphVolunteerId].
final volunteerTasksForSessionProvider = FutureProvider<List<VolunteerTaskItemDto>>((ref) async {
  final storage = ref.watch(storageServiceProvider);
  final id = await storage.getString(SessionKeys.graphVolunteerId);
  if (id == null || id.isEmpty) {
    throw Exception('Register or sign in as a volunteer to load tasks.');
  }
  final usecase = ref.watch(getVolunteerTasksUsecaseProvider);
  final result = await usecase.call(id);
  return switch (result) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});

/// Profile (credits, trust) for session volunteer, or null if not a volunteer session.
final volunteerProfileBySessionProvider = FutureProvider<VolunteerProfileDto?>((ref) async {
  final storage = ref.watch(storageServiceProvider);
  final id = await storage.getString(SessionKeys.graphVolunteerId);
  if (id == null || id.isEmpty) {
    return null;
  }
  final repo = ref.watch(volunteerTasksRepositoryProvider);
  final result = await repo.getVolunteer(id);
  return switch (result) {
    Success(:final data) => data,
    Failure() => null,
  };
});

void invalidateVolunteerTaskCaches(WidgetRef ref, {required String incidentId}) {
  ref.invalidate(volunteerTasksForSessionProvider);
  ref.invalidate(volunteerProfileBySessionProvider);
  ref.invalidate(incidentDetailProvider(incidentId));
  ref.invalidate(volunteerGuidanceProvider(incidentId));
  ref.invalidate(dashboardSummaryProvider);
}
