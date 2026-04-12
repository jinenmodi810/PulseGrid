class HospitalModel {
  const HospitalModel({
    required this.id,
    required this.name,
    required this.bedsAvailable,
    this.latitude,
    this.longitude,
  });

  final String id;
  final String name;
  final int bedsAvailable;
  final double? latitude;
  final double? longitude;

  factory HospitalModel.fromJson(Map<String, dynamic> json) {
    return HospitalModel(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? 'Hospital',
      bedsAvailable: (json['beds_available'] as num?)?.toInt() ?? 0,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
    );
  }
}
