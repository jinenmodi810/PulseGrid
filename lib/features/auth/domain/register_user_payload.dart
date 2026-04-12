class RegisterUserPayload {
  const RegisterUserPayload({
    required this.email,
    required this.password,
    required this.fullName,
    required this.phone,
    required this.preferredLanguage,
    required this.homeZoneId,
    this.householdSize,
    this.elderlyCount = 0,
    this.mobilityConcern = false,
    this.oxygenDependency = false,
    required this.emergencyContactName,
    required this.emergencyContactPhone,
    this.emergencyContactRelationship = '',
  });

  final String email;
  final String password;
  final String fullName;
  final String phone;
  final String preferredLanguage;
  final String homeZoneId;
  final int? householdSize;
  final int elderlyCount;
  final bool mobilityConcern;
  final bool oxygenDependency;
  final String emergencyContactName;
  final String emergencyContactPhone;
  final String emergencyContactRelationship;

  Map<String, dynamic> toJson() => {
        'email': email,
        'password': password,
        'full_name': fullName,
        'phone': phone,
        'preferred_language': preferredLanguage,
        'home_zone_id': homeZoneId,
        'household_size': householdSize,
        'elderly_count': elderlyCount,
        'mobility_concern': mobilityConcern,
        'oxygen_dependency': oxygenDependency,
        'emergency_contact_name': emergencyContactName,
        'emergency_contact_phone': emergencyContactPhone,
        'emergency_contact_relationship': emergencyContactRelationship,
      };
}
