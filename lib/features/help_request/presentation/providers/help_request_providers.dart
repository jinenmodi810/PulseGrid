import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/providers.dart';
import '../../../../core/utils/result.dart';
import '../../application/get_incident_tracking_usecase.dart';
import '../../application/preview_help_priority_usecase.dart';
import '../../application/submit_help_request_usecase.dart';
import '../../data/help_request_repository.dart';
import '../../../incident_tracking/data/incident_detail_dto.dart';

final helpRequestRepositoryProvider = Provider<HelpRequestRepository>((ref) {
  return HelpRequestRepository(ref.watch(apiClientProvider));
});

final previewHelpPriorityUsecaseProvider = Provider<PreviewHelpPriorityUsecase>((ref) {
  return PreviewHelpPriorityUsecase(ref.watch(helpRequestRepositoryProvider));
});

final submitHelpRequestUsecaseProvider = Provider<SubmitHelpRequestUsecase>((ref) {
  return SubmitHelpRequestUsecase(
    ref.watch(helpRequestRepositoryProvider),
    ref.watch(storageServiceProvider),
  );
});

final getIncidentTrackingUsecaseProvider = Provider<GetIncidentTrackingUsecase>((ref) {
  return GetIncidentTrackingUsecase(ref.watch(helpRequestRepositoryProvider));
});

/// Last submitted incident id from local session (may be stale).
final victimLastIncidentIdProvider = FutureProvider<String?>((ref) async {
  final s = ref.watch(storageServiceProvider);
  final v = await s.getString(SessionKeys.lastIncidentId);
  if (v == null || v.isEmpty) {
    return null;
  }
  return v;
});

final incidentDetailProvider = FutureProvider.family<IncidentDetailDto, String>((ref, incidentId) async {
  final usecase = ref.watch(getIncidentTrackingUsecaseProvider);
  final result = await usecase.call(incidentId);
  return switch (result) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});
