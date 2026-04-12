// TODO(Phase1): Replace mock data with API integration via ApiClient.

import '../../app/constants/app_constants.dart';
import '../../core/utils/result.dart';
import '../../core/services/mock_data_service.dart';
import '../models/hospital_model.dart';

class HospitalRepository {
  HospitalRepository(this._mockData);

  final MockDataService _mockData;

  Future<Result<List<HospitalModel>, String>> getHospitals() async {
    try {
      final rows = await _mockData.decodeList(AssetPaths.mockHospitals);
      final models = rows
          .whereType<Map<String, dynamic>>()
          .map(HospitalModel.fromJson)
          .toList(growable: false);
      return Success(models);
    } catch (e) {
      return Failure(e.toString());
    }
  }
}
