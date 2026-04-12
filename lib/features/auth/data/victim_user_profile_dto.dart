/// Affected-user profile from `GET /users/{user_id}`.
class VictimUserProfileDto {
  const VictimUserProfileDto({
    required this.userId,
    this.email = '',
    required this.fullName,
    required this.phone,
    required this.preferredLanguage,
    required this.zoneId,
    required this.householdSize,
    required this.elderlyCount,
    required this.mobilityConcern,
    required this.oxygenDependency,
    required this.emergencyContactName,
    required this.emergencyContactPhone,
    required this.emergencyContactRelationship,
  });

  final String userId;
  final String email;
  final String fullName;
  final String phone;
  final String preferredLanguage;
  final String zoneId;
  final int householdSize;
  final int elderlyCount;
  final bool mobilityConcern;
  final bool oxygenDependency;
  final String emergencyContactName;
  final String emergencyContactPhone;
  final String emergencyContactRelationship;

  factory VictimUserProfileDto.fromJson(Map<String, dynamic> json) {
    return VictimUserProfileDto(
      userId: json['user_id'] as String? ?? '',
      email: json['email'] as String? ?? '',
      fullName: json['full_name'] as String? ?? '',
      phone: json['phone'] as String? ?? '',
      preferredLanguage: json['preferred_language'] as String? ?? 'en',
      zoneId: json['zone_id'] as String? ?? '',
      householdSize: (json['household_size'] as num?)?.toInt() ?? 1,
      elderlyCount: (json['elderly_count'] as num?)?.toInt() ?? 0,
      mobilityConcern: json['mobility_concern'] as bool? ?? false,
      oxygenDependency: json['oxygen_dependency'] as bool? ?? false,
      emergencyContactName: json['emergency_contact_name'] as String? ?? '',
      emergencyContactPhone: json['emergency_contact_phone'] as String? ?? '',
      emergencyContactRelationship: json['emergency_contact_relationship'] as String? ?? '',
    );
  }
}
