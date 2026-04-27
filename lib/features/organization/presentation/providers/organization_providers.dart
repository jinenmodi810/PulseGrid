import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../app/providers.dart';
import '../../../../core/utils/result.dart';
import '../../data/organization_dtos.dart';
import '../../data/organization_repository.dart';

final organizationRepositoryProvider = Provider<OrganizationRepository>((ref) {
  return OrganizationRepository(ref.watch(apiClientProvider), ref.watch(storageServiceProvider));
});

final organizationSessionIdProvider = FutureProvider<String>((ref) async {
  final id = await ref.watch(organizationRepositoryProvider).sessionOrganizationId();
  if (id == null || id.isEmpty) {
    throw Exception('Register as an organization to continue.');
  }
  return id;
});

final organizationOverviewProvider = FutureProvider.autoDispose<OrganizationOverviewDto>((ref) async {
  final oid = await ref.watch(organizationSessionIdProvider.future);
  final r = await ref.watch(organizationRepositoryProvider).getOverview(oid);
  return switch (r) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});

final organizationIncidentsProvider = FutureProvider.autoDispose<List<OrganizationIncidentRowDto>>((ref) async {
  final oid = await ref.watch(organizationSessionIdProvider.future);
  final r = await ref.watch(organizationRepositoryProvider).listIncidents(oid);
  return switch (r) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});

class OrganizationAnalyticsBundle {
  const OrganizationAnalyticsBundle({
    required this.overview,
    required this.incidentsByZone,
    required this.timeToResponse,
    required this.capacity,
  });

  final AnalyticsOverviewDto overview;
  final List<IncidentsByZoneDto> incidentsByZone;
  final TimeToResponseDto timeToResponse;
  final List<OrganizationCapacityAnalyticsDto> capacity;
}

final organizationAnalyticsProvider = FutureProvider.autoDispose<OrganizationAnalyticsBundle>((ref) async {
  final repo = ref.watch(organizationRepositoryProvider);
  final orgOverview = await ref.watch(organizationOverviewProvider.future);
  final oid = orgOverview.organizationId;
  final zoneId = orgOverview.zoneId;

  final overviewR = await repo.getAnalyticsOverview(zoneId: zoneId);
  final zoneR = await repo.getIncidentsByZone(zoneId: zoneId);
  final ttrR = await repo.getTimeToResponse(zoneId: zoneId);
  final capR = await repo.getOrganizationCapacityAnalytics(oid);

  final overview = switch (overviewR) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
  final incidentsByZone = switch (zoneR) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
  final timeToResponse = switch (ttrR) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
  final capacity = switch (capR) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
  return OrganizationAnalyticsBundle(
    overview: overview,
    incidentsByZone: incidentsByZone,
    timeToResponse: timeToResponse,
    capacity: capacity,
  );
});
