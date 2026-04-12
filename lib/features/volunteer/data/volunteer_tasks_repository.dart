import 'package:dio/dio.dart';

import '../../../core/utils/result.dart';
import '../../../data/sources/remote/api_client.dart';
import 'volunteer_task_item_dto.dart';

class VolunteerTasksRepository {
  VolunteerTasksRepository(this._api);

  final ApiClient _api;

  String _dioMessage(DioException e) {
    if (e.type == DioExceptionType.connectionError) {
      return "We can't reach PulseGrid right now. Check that the API is running.";
    }
    if (e.type == DioExceptionType.connectionTimeout || e.type == DioExceptionType.receiveTimeout) {
      return 'The server took too long to respond. Try again.';
    }
    final data = e.response?.data;
    if (data is Map && data['detail'] != null) {
      return data['detail'].toString();
    }
    return e.message ?? 'Something went wrong.';
  }

  Future<Result<List<VolunteerTaskItemDto>, String>> getTasks(String volunteerId) async {
    try {
      final res = await _api.client.get<List<dynamic>>('/volunteers/$volunteerId/tasks');
      final data = res.data;
      if (data == null) {
        return const Success([]);
      }
      final out = <VolunteerTaskItemDto>[];
      for (final item in data) {
        if (item is Map<String, dynamic>) {
          out.add(VolunteerTaskItemDto.fromJson(item));
        }
      }
      return Success(out);
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<VolunteerProfileDto, String>> getVolunteer(String volunteerId) async {
    try {
      final res = await _api.client.get<Map<String, dynamic>>('/volunteers/$volunteerId');
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(VolunteerProfileDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<AcceptTaskResultDto, String>> acceptTask({
    required String incidentId,
    required String volunteerId,
  }) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/incidents/$incidentId/accept',
        data: {'volunteer_id': volunteerId},
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(AcceptTaskResultDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<CompleteTaskResultDto, String>> completeTask({
    required String incidentId,
    required String volunteerId,
  }) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/incidents/$incidentId/complete',
        data: {'volunteer_id': volunteerId},
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(CompleteTaskResultDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }
}
