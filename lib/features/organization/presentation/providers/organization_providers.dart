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
