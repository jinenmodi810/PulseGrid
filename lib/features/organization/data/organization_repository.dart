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
}
