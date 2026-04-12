class RouteEdgeModel {
  const RouteEdgeModel({
    required this.id,
    required this.fromId,
    required this.toId,
    required this.distanceKm,
    required this.etaMinutes,
  });

  final String id;
  final String fromId;
  final String toId;
  final double distanceKm;
  final int etaMinutes;

  factory RouteEdgeModel.fromJson(Map<String, dynamic> json) {
    return RouteEdgeModel(
      id: json['id'] as String? ?? '',
      fromId: json['from_id'] as String? ?? '',
      toId: json['to_id'] as String? ?? '',
      distanceKm: (json['distance_km'] as num?)?.toDouble() ?? 0,
      etaMinutes: (json['eta_minutes'] as num?)?.toInt() ?? 0,
    );
  }
}
