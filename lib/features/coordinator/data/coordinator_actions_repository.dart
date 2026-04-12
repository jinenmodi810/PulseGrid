import 'package:dio/dio.dart';

import '../../../core/utils/result.dart';
import '../../../data/sources/remote/api_client.dart';

class CoordinatorIncidentActionDto {
  const CoordinatorIncidentActionDto({
    required this.incidentId,
    required this.status,
    this.routeStatus,
  });

  final String incidentId;
  final String status;
  final String? routeStatus;

  factory CoordinatorIncidentActionDto.fromJson(Map<String, dynamic> json) {
    return CoordinatorIncidentActionDto(
      incidentId: json['incident_id'] as String? ?? '',
      status: json['status'] as String? ?? '',
      routeStatus: json['route_status'] as String?,
    );
  }
}

class CoordinatorActionsRepository {
  CoordinatorActionsRepository(this._api);

  final ApiClient _api;

  String _dioMessage(DioException e) {
    if (e.type == DioExceptionType.connectionError) {
      return "We can't reach PulseGrid right now. Check that the API is running.";
    }
    final data = e.response?.data;
    if (data is Map && data['detail'] != null) {
      return data['detail'].toString();
    }
    return e.message ?? 'Something went wrong.';
  }

  Future<Result<CoordinatorIncidentActionDto, String>> reassign({
    required String incidentId,
    required String newVolunteerId,
  }) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/incidents/$incidentId/reassign',
        data: {'new_volunteer_id': newVolunteerId},
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(CoordinatorIncidentActionDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<CoordinatorIncidentActionDto, String>> escalate({
    required String incidentId,
    String note = '',
  }) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/incidents/$incidentId/escalate',
        data: {'note': note},
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(CoordinatorIncidentActionDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<CoordinatorIncidentActionDto, String>> blockRoute({
    required String incidentId,
    String reason = '',
  }) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/incidents/$incidentId/block-route',
        data: {'note': reason},
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(CoordinatorIncidentActionDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }
}
