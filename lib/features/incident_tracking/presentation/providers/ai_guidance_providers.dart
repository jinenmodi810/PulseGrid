import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/providers.dart';
import '../../../../core/utils/result.dart';
import '../../application/get_affected_user_guidance_usecase.dart';
import '../../data/ai_guidance_repository.dart';
import '../../../volunteer/application/get_volunteer_guidance_usecase.dart';
import '../../../organization/application/get_organization_incident_summary_usecase.dart';

final aiGuidanceRepositoryProvider = Provider<AiGuidanceRepository>((ref) {
  return AiGuidanceRepository(ref.watch(apiClientProvider));
});

final getAffectedUserGuidanceUsecaseProvider = Provider<GetAffectedUserGuidanceUsecase>((ref) {
  return GetAffectedUserGuidanceUsecase(ref.watch(aiGuidanceRepositoryProvider));
});

final getVolunteerGuidanceUsecaseProvider = Provider<GetVolunteerGuidanceUsecase>((ref) {
  return GetVolunteerGuidanceUsecase(ref.watch(aiGuidanceRepositoryProvider));
});

final getOrganizationIncidentSummaryUsecaseProvider = Provider<GetOrganizationIncidentSummaryUsecase>((ref) {
  return GetOrganizationIncidentSummaryUsecase(ref.watch(aiGuidanceRepositoryProvider));
});

/// Gemini-backed calm guidance for the affected user (refreshed with [ref.invalidate]).
final affectedUserGuidanceProvider = FutureProvider.autoDispose.family<GuidanceDto, String>((ref, incidentId) async {
  final uc = ref.watch(getAffectedUserGuidanceUsecaseProvider);
  final r = await uc.call(incidentId);
  return switch (r) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});

/// Operational instructions for the volunteer on this incident.
final volunteerGuidanceProvider = FutureProvider.autoDispose.family<GuidanceDto, String>((ref, incidentId) async {
  final storage = ref.watch(storageServiceProvider);
  final vid = await storage.getString(SessionKeys.graphVolunteerId);
  final uc = ref.watch(getVolunteerGuidanceUsecaseProvider);
  final r = await uc.call(incidentId: incidentId, volunteerId: vid);
  return switch (r) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});

/// AI-assisted operational summary for an incident (organization console / deep links).
final organizationIncidentSummaryProvider = FutureProvider.autoDispose.family<GuidanceDto, String>((ref, incidentId) async {
  final uc = ref.watch(getOrganizationIncidentSummaryUsecaseProvider);
  final r = await uc.call(incidentId);
  return switch (r) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});
