import 'package:dio/dio.dart';

import '../../core/utils/result.dart';
import '../sources/remote/api_client.dart';
import '../models/support_contact_model.dart';

class SupportRepository {
  SupportRepository(this._api);

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

  Future<Result<List<SupportContactModel>, String>> getContacts() async {
    try {
      final res = await _api.client.get<List<dynamic>>('/support/contacts');
      final data = res.data;
      if (data == null) {
        return const Success([]);
      }
      final out = <SupportContactModel>[];
      for (final item in data) {
        if (item is Map<String, dynamic>) {
          out.add(SupportContactModel.fromJson(item));
        }
      }
      return Success(out);
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }
}
