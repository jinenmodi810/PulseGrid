import 'package:dio/dio.dart';

import '../../../app/constants/app_constants.dart';
import '../../../core/services/storage_service.dart';
import '../../../core/utils/result.dart';
import '../../../data/sources/remote/api_client.dart';
import 'admin_inspection_dtos.dart';

class AdminInspectionRepository {
  AdminInspectionRepository(this._api, this._storage);

  final ApiClient _api;
  final StorageService _storage;

  static const _header = 'X-Admin-Session';

  Future<String?> _marker() => _storage.getString(SessionKeys.adminMarker);

  Future<Map<String, String>> _headers() async {
    final m = await _marker();
    if (m == null || m.isEmpty) {
      return {};
    }
    return {_header: m};
  }

  String _dioMessage(DioException e) {
    if (e.type == DioExceptionType.connectionError) {
      return "We can't reach the PulseGrid API. Check the server and network.";
    }
    if (e.type == DioExceptionType.connectionTimeout || e.type == DioExceptionType.receiveTimeout) {
      return 'The server took too long to respond. Try again.';
    }
    if (e.response?.statusCode == 401) {
      return 'Admin session expired or missing. Sign in again from the coordinator login.';
    }
    final data = e.response?.data;
    if (data is Map && data['detail'] != null) {
      return data['detail'].toString();
    }
    return e.message ?? 'Request failed.';
  }

  Future<Result<List<T>, String>> _getList<T>(
    String path,
    T Function(Map<String, dynamic>) fromJson,
  ) async {
    try {
      final headers = await _headers();
      if (!headers.containsKey(_header)) {
        return const Failure('Coordinator session not found. Sign in again.');
      }
      final res = await _api.client.get<List<dynamic>>(path, options: Options(headers: headers));
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      final list = data.map((e) => fromJson(Map<String, dynamic>.from(e as Map))).toList();
      return Success(list);
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<AdminOverviewDto, String>> getOverview() async {
    try {
      final headers = await _headers();
      if (!headers.containsKey(_header)) {
        return const Failure('Coordinator session not found. Sign in again.');
      }
      final res = await _api.client.get<Map<String, dynamic>>(
        '/admin/overview',
        options: Options(headers: headers),
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(AdminOverviewDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<List<AdminUserDto>, String>> getUsers() async {
    return _getList('/admin/users', AdminUserDto.fromJson);
  }

  Future<Result<List<AdminVolunteerDto>, String>> getVolunteers() async {
    return _getList('/admin/volunteers', AdminVolunteerDto.fromJson);
  }

  Future<Result<List<AdminIncidentDto>, String>> getIncidents() async {
    return _getList('/admin/incidents', AdminIncidentDto.fromJson);
  }

  Future<Result<AdminIncidentDetailDto, String>> getIncidentDetail(String incidentId) async {
    try {
      final headers = await _headers();
      if (!headers.containsKey(_header)) {
        return const Failure('Coordinator session not found. Sign in again.');
      }
      final res = await _api.client.get<Map<String, dynamic>>(
        '/admin/incidents/$incidentId',
        options: Options(headers: headers),
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(AdminIncidentDetailDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<List<AdminAssignmentDto>, String>> getAssignments() async {
    return _getList('/admin/assignments', AdminAssignmentDto.fromJson);
  }

  Future<Result<List<AdminRewardDto>, String>> getRewards() async {
    return _getList('/admin/rewards', AdminRewardDto.fromJson);
  }

  Future<Result<AdminSupportNetworkDto, String>> getSupportNetwork() async {
    try {
      final headers = await _headers();
      if (!headers.containsKey(_header)) {
        return const Failure('Coordinator session not found. Sign in again.');
      }
      final res = await _api.client.get<Map<String, dynamic>>(
        '/admin/support-network',
        options: Options(headers: headers),
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(AdminSupportNetworkDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }
}
