// TODO(Phase1): Replace mock data with API integration via ApiClient.

import '../../app/constants/app_constants.dart';
import '../../core/utils/result.dart';
import '../../core/services/mock_data_service.dart';
import '../models/responder_model.dart';

class ResponderRepository {
  ResponderRepository(this._mockData);

  final MockDataService _mockData;

  Future<Result<List<ResponderModel>, String>> getResponders() async {
    try {
      final rows = await _mockData.decodeList(AssetPaths.mockResponders);
      final models = rows
          .whereType<Map<String, dynamic>>()
          .map(ResponderModel.fromJson)
          .toList(growable: false);
      return Success(models);
    } catch (e) {
      return Failure(e.toString());
    }
  }
}
