import 'package:dio/dio.dart';

import '../../../app/constants/app_constants.dart';
import '../../../core/services/storage_service.dart';
import '../../../core/utils/result.dart';
import '../../../data/sources/remote/api_client.dart';
import 'organization_dtos.dart';

class OrganizationRepository {
  OrganizationRepository(this._api, this._storage);

  final ApiClient _api;
  final StorageService _storage;

  Future<String?> _orgId() => _storage.getString(SessionKeys.graphOrganizationId);

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

  String _analyticsMessage(DioException e) {
    final status = e.response?.statusCode;
    final data = e.response?.data;
    if (status == 503) {
      final detail = data is Map ? data['detail']?.toString() : null;
      if (detail != null && detail.toLowerCase().contains('gold')) {
        return 'Analytics will appear after operational data is processed.';
      }
      return 'Analytics will appear after operational data is processed.';
    }
    return _dioMessage(e);
  }

  Future<Result<OrganizationOverviewDto, String>> getOverview(String organizationId) async {
    try {
      final res = await _api.client.get<Map<String, dynamic>>('/organizations/$organizationId/overview');
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(OrganizationOverviewDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<List<OrganizationIncidentRowDto>, String>> listIncidents(String organizationId) async {
    try {
      final res = await _api.client.get<List<dynamic>>('/organizations/$organizationId/incidents');
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      final list = data.map((e) => OrganizationIncidentRowDto.fromJson(Map<String, dynamic>.from(e as Map))).toList();
      return Success(list);
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<void, String>> updateCapacity(String organizationId, Map<String, dynamic> body) async {
    try {
      await _api.client.post<void>('/organizations/$organizationId/capacity-update', data: body);
      return const Success(null);
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<void, String>> acceptIncident(String organizationId, String incidentId) async {
    try {
      await _api.client.post<void>(
        '/organizations/$organizationId/accept-incident',
        data: {'incident_id': incidentId},
      );
      return const Success(null);
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<void, String>> updateResponseStatus(
    String organizationId, {
    required String incidentId,
    required String status,
  }) async {
    try {
      await _api.client.post<void>(
        '/organizations/$organizationId/update-response-status',
        data: {'incident_id': incidentId, 'status': status},
      );
      return const Success(null);
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<String?> sessionOrganizationId() => _orgId();

  Future<Result<AnalyticsOverviewDto, String>> getAnalyticsOverview({
    String? zoneId,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final qp = <String, dynamic>{};
      if (zoneId != null && zoneId.isNotEmpty) qp['zone_id'] = zoneId;
      if (startDate != null && startDate.isNotEmpty) qp['start_date'] = startDate;
      if (endDate != null && endDate.isNotEmpty) qp['end_date'] = endDate;
      final res = await _api.client.get<Map<String, dynamic>>('/analytics/overview', queryParameters: qp);
      final data = res.data;
      if (data == null) return const Failure('Empty analytics response');
      return Success(AnalyticsOverviewDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_analyticsMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<List<IncidentsByZoneDto>, String>> getIncidentsByZone({
    String? zoneId,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final qp = <String, dynamic>{};
      if (zoneId != null && zoneId.isNotEmpty) qp['zone_id'] = zoneId;
      if (startDate != null && startDate.isNotEmpty) qp['start_date'] = startDate;
      if (endDate != null && endDate.isNotEmpty) qp['end_date'] = endDate;
      final res = await _api.client.get<List<dynamic>>('/analytics/incidents-by-zone', queryParameters: qp);
      final data = res.data ?? const [];
      final rows = data
          .map((e) => IncidentsByZoneDto.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(growable: false);
      return Success(rows);
    } on DioException catch (e) {
      return Failure(_analyticsMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<TimeToResponseDto, String>> getTimeToResponse({
    String? zoneId,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final qp = <String, dynamic>{};
      if (zoneId != null && zoneId.isNotEmpty) qp['zone_id'] = zoneId;
      if (startDate != null && startDate.isNotEmpty) qp['start_date'] = startDate;
      if (endDate != null && endDate.isNotEmpty) qp['end_date'] = endDate;
      final res = await _api.client.get<Map<String, dynamic>>('/analytics/time-to-response', queryParameters: qp);
      final data = res.data;
      if (data == null) return const Failure('Empty time-to-response response');
      return Success(TimeToResponseDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_analyticsMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<List<OrganizationCapacityAnalyticsDto>, String>> getOrganizationCapacityAnalytics(
    String organizationId, {
    String? startDate,
    String? endDate,
  }) async {
    try {
      final qp = <String, dynamic>{'organization_id': organizationId};
      if (startDate != null && startDate.isNotEmpty) qp['start_date'] = startDate;
      if (endDate != null && endDate.isNotEmpty) qp['end_date'] = endDate;
      final res = await _api.client.get<List<dynamic>>('/analytics/organization-capacity', queryParameters: qp);
      final data = res.data ?? const [];
      final rows = data
          .map((e) => OrganizationCapacityAnalyticsDto.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(growable: false);
      return Success(rows);
    } on DioException catch (e) {
      return Failure(_analyticsMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }
}
