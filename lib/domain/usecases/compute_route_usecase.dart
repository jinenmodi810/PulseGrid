import '../../data/models/route_edge_model.dart';

class ComputeRouteUseCase {
  const ComputeRouteUseCase();

  // TODO(Phase1): replace with graph search / external routing API.
  List<RouteEdgeModel> call({required List<RouteEdgeModel> edges, required String startId}) {
    return edges.where((e) => e.fromId == startId).toList(growable: false);
  }
}
