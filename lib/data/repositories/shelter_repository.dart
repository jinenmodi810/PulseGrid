// TODO(Phase1): Replace mock data with API integration via ApiClient.

import '../../app/constants/app_constants.dart';
import '../../core/utils/result.dart';
import '../../core/services/mock_data_service.dart';
import '../models/shelter_model.dart';

class ShelterRepository {
  ShelterRepository(this._mockData);

  final MockDataService _mockData;

  Future<Result<List<ShelterModel>, String>> getShelters() async {
    try {
      final rows = await _mockData.decodeList(AssetPaths.mockShelters);
      final models = rows
          .whereType<Map<String, dynamic>>()
          .map(ShelterModel.fromJson)
          .toList(growable: false);
      return Success(models);
    } catch (e) {
      return Failure(e.toString());
    }
  }
}
