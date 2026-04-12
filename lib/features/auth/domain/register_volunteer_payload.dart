class RegisterVolunteerPayload {
  const RegisterVolunteerPayload({
    required this.email,
    required this.password,
    required this.fullName,
    required this.phone,
    required this.languages,
    required this.zoneId,
    required this.availability,
    required this.transportAccess,
    required this.skills,
    required this.supportTypes,
    required this.verified,
  });

  final String email;
  final String password;
  final String fullName;
  final String phone;
  final List<String> languages;
  final String zoneId;
  final String availability;
  final String transportAccess;
  final List<String> skills;
  final List<String> supportTypes;
  final bool verified;

  Map<String, dynamic> toJson() => {
        'email': email,
        'password': password,
        'full_name': fullName,
        'phone': phone,
        'languages': languages,
        'zone_id': zoneId,
        'availability': availability,
        'transport_access': transportAccess,
        'skills': skills,
        'support_types': supportTypes,
        'verified': verified,
      };
}
