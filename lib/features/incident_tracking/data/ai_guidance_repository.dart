import 'package:dio/dio.dart';

import '../../../core/utils/result.dart';
import '../../../data/sources/remote/api_client.dart';

class GuidanceDto {
  const GuidanceDto({
    required this.role,
    required this.language,
    required this.message,
    required this.fallbackUsed,
    this.generatedAt,
  });

  final String role;
  final String language;
  final String message;
  final bool fallbackUsed;
  final String? generatedAt;

  factory GuidanceDto.fromJson(Map<String, dynamic> json) {
    return GuidanceDto(
      role: json['role'] as String? ?? '',
      language: json['language'] as String? ?? 'en',
      message: json['message'] as String? ?? '',
      fallbackUsed: json['fallback_used'] as bool? ?? false,
      generatedAt: json['generated_at'] as String?,
    );
  }
}

class IncidentGuidanceBundleDto {
  const IncidentGuidanceBundleDto({
    required this.incidentId,
    required this.affectedUser,
    this.coordinatorSummary,
  });

  final String incidentId;
  final GuidanceDto affectedUser;
  final GuidanceDto? coordinatorSummary;

  factory IncidentGuidanceBundleDto.fromJson(Map<String, dynamic> json) {
    final aff = json['affected_user'];
    final coord = json['coordinator_summary'];
    return IncidentGuidanceBundleDto(
      incidentId: json['incident_id'] as String? ?? '',
      affectedUser: aff is Map<String, dynamic> ? GuidanceDto.fromJson(aff) : const GuidanceDto(role: '', language: 'en', message: '', fallbackUsed: true),
      coordinatorSummary: coord is Map<String, dynamic> ? GuidanceDto.fromJson(coord) : null,
    );
  }
}

class AiGuidanceRepository {
  AiGuidanceRepository(this._api);

  final ApiClient _api;

  String _dioMessage(DioException e) {
    if (e.type == DioExceptionType.connectionError) {
      return "We can't reach the PulseGrid API right now.";
    }
    if (e.type == DioExceptionType.connectionTimeout || e.type == DioExceptionType.receiveTimeout) {
      return 'The server took too long to respond.';
    }
    final data = e.response?.data;
    if (data is Map && data['detail'] != null) {
      return data['detail'].toString();
    }
    return e.message ?? 'Request failed.';
  }

  Future<Result<IncidentGuidanceBundleDto, String>> getIncidentGuidance({
    required String incidentId,
    bool includeCoordinator = false,
  }) async {
    try {
      final res = await _api.client.get<Map<String, dynamic>>(
        '/ai/incidents/$incidentId/guidance',
        queryParameters: {'include_coordinator': includeCoordinator},
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(IncidentGuidanceBundleDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<GuidanceDto, String>> postVolunteerGuidance({
    required String incidentId,
    String? volunteerId,
  }) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/ai/guidance/volunteer',
        data: {
          'incident_id': incidentId,
          if (volunteerId != null && volunteerId.isNotEmpty) 'volunteer_id': volunteerId,
        },
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(GuidanceDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<GuidanceDto, String>> postCoordinatorSummary({required String incidentId}) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/ai/guidance/coordinator-summary',
        data: {'incident_id': incidentId},
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(GuidanceDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }
}
