// TODO(Phase1): Replace mock data with API integration via ApiClient.

import '../../app/constants/app_constants.dart';
import '../../core/utils/result.dart';
import '../../core/services/mock_data_service.dart';
import '../models/route_edge_model.dart';

class RoutingRepository {
  RoutingRepository(this._mockData);

  final MockDataService _mockData;

  Future<Result<List<RouteEdgeModel>, String>> getRouteEdges() async {
    try {
      final rows = await _mockData.decodeList(AssetPaths.mockRoutes);
      final models = rows
          .whereType<Map<String, dynamic>>()
          .map(RouteEdgeModel.fromJson)
          .toList(growable: false);
      return Success(models);
    } catch (e) {
      return Failure(e.toString());
    }
  }
}
