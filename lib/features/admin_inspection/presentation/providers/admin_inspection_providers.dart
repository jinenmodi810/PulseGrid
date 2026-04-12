import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../app/providers.dart';
import '../../../../core/utils/result.dart';
import '../../application/get_admin_assignments_usecase.dart';
import '../../application/get_admin_incident_detail_usecase.dart';
import '../../application/get_admin_incidents_usecase.dart';
import '../../application/get_admin_overview_usecase.dart';
import '../../application/get_admin_rewards_usecase.dart';
import '../../application/get_admin_support_network_usecase.dart';
import '../../application/get_admin_users_usecase.dart';
import '../../application/get_admin_volunteers_usecase.dart';
import '../../data/admin_inspection_dtos.dart';
import '../../data/admin_inspection_repository.dart';

final adminInspectionRepositoryProvider = Provider<AdminInspectionRepository>((ref) {
  return AdminInspectionRepository(
    ref.watch(apiClientProvider),
    ref.watch(storageServiceProvider),
  );
});

final getAdminOverviewUsecaseProvider = Provider<GetAdminOverviewUsecase>((ref) {
  return GetAdminOverviewUsecase(ref.watch(adminInspectionRepositoryProvider));
});

final getAdminUsersUsecaseProvider = Provider<GetAdminUsersUsecase>((ref) {
  return GetAdminUsersUsecase(ref.watch(adminInspectionRepositoryProvider));
});

final getAdminVolunteersUsecaseProvider = Provider<GetAdminVolunteersUsecase>((ref) {
  return GetAdminVolunteersUsecase(ref.watch(adminInspectionRepositoryProvider));
});

final getAdminIncidentsUsecaseProvider = Provider<GetAdminIncidentsUsecase>((ref) {
  return GetAdminIncidentsUsecase(ref.watch(adminInspectionRepositoryProvider));
});

final getAdminIncidentDetailUsecaseProvider = Provider<GetAdminIncidentDetailUsecase>((ref) {
  return GetAdminIncidentDetailUsecase(ref.watch(adminInspectionRepositoryProvider));
});

final getAdminAssignmentsUsecaseProvider = Provider<GetAdminAssignmentsUsecase>((ref) {
  return GetAdminAssignmentsUsecase(ref.watch(adminInspectionRepositoryProvider));
});

final getAdminRewardsUsecaseProvider = Provider<GetAdminRewardsUsecase>((ref) {
  return GetAdminRewardsUsecase(ref.watch(adminInspectionRepositoryProvider));
});

final getAdminSupportNetworkUsecaseProvider = Provider<GetAdminSupportNetworkUsecase>((ref) {
  return GetAdminSupportNetworkUsecase(ref.watch(adminInspectionRepositoryProvider));
});

final adminOverviewProvider = FutureProvider.autoDispose<AdminOverviewDto>((ref) async {
  final r = await ref.watch(getAdminOverviewUsecaseProvider).call();
  return switch (r) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});

final adminUsersProvider = FutureProvider.autoDispose<List<AdminUserDto>>((ref) async {
  final r = await ref.watch(getAdminUsersUsecaseProvider).call();
  return switch (r) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});

final adminVolunteersProvider = FutureProvider.autoDispose<List<AdminVolunteerDto>>((ref) async {
  final r = await ref.watch(getAdminVolunteersUsecaseProvider).call();
  return switch (r) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});

final adminIncidentsProvider = FutureProvider.autoDispose<List<AdminIncidentDto>>((ref) async {
  final r = await ref.watch(getAdminIncidentsUsecaseProvider).call();
  return switch (r) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});

final adminIncidentDetailProvider =
    FutureProvider.autoDispose.family<AdminIncidentDetailDto, String>((ref, incidentId) async {
  final r = await ref.watch(getAdminIncidentDetailUsecaseProvider).call(incidentId);
  return switch (r) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});

final adminAssignmentsProvider = FutureProvider.autoDispose<List<AdminAssignmentDto>>((ref) async {
  final r = await ref.watch(getAdminAssignmentsUsecaseProvider).call();
  return switch (r) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});

final adminRewardsProvider = FutureProvider.autoDispose<List<AdminRewardDto>>((ref) async {
  final r = await ref.watch(getAdminRewardsUsecaseProvider).call();
  return switch (r) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});

final adminSupportNetworkProvider = FutureProvider.autoDispose<AdminSupportNetworkDto>((ref) async {
  final r = await ref.watch(getAdminSupportNetworkUsecaseProvider).call();
  return switch (r) {
    Success(:final data) => data,
    Failure(:final error) => throw Exception(error),
  };
});
