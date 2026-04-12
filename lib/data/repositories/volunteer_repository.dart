// TODO(Phase1): Replace mock data with API integration via ApiClient.

import '../../app/constants/app_constants.dart';
import '../../core/utils/result.dart';
import '../../core/services/mock_data_service.dart';
import '../models/volunteer_model.dart';

class VolunteerRepository {
  VolunteerRepository(this._mockData);

  final MockDataService _mockData;

  Future<Result<List<VolunteerModel>, String>> getVolunteers() async {
    try {
      final rows = await _mockData.decodeList(AssetPaths.mockVolunteers);
      final models = rows
          .whereType<Map<String, dynamic>>()
          .map(VolunteerModel.fromJson)
          .toList(growable: false);
      return Success(models);
    } catch (e) {
      return Failure(e.toString());
    }
  }
}
