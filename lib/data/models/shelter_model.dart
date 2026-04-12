class ShelterModel {
  const ShelterModel({
    required this.id,
    required this.name,
    required this.capacity,
    required this.occupancy,
    this.latitude,
    this.longitude,
  });

  final String id;
  final String name;
  final int capacity;
  final int occupancy;
  final double? latitude;
  final double? longitude;

  factory ShelterModel.fromJson(Map<String, dynamic> json) {
    return ShelterModel(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? 'Shelter',
      capacity: (json['capacity'] as num?)?.toInt() ?? 0,
      occupancy: (json['occupancy'] as num?)?.toInt() ?? 0,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
    );
  }
}
