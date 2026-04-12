import '../../../core/enums/user_role.dart';

/// Flattened `GET /auth/me` payload.
class AuthMeDto {
  const AuthMeDto({
    required this.role,
    required this.id,
    required this.email,
    this.fullName,
    this.phone,
    this.zoneId,
    this.preferredLanguage,
    this.householdSize,
    this.elderlyCount,
    this.mobilityConcern,
    this.oxygenDependency,
    this.emergencyContactName,
    this.emergencyContactPhone,
    this.emergencyContactRelationship,
    this.organizationName,
    this.orgType,
    this.contactName,
    this.contactPhone,
    this.skills,
    this.supportTypes,
    this.languages,
    this.transportAccess,
    this.availability,
    this.credits,
    this.trustScore,
  });

  final String role;
  final String id;
  final String email;
  final String? fullName;
  final String? phone;
  final String? zoneId;
  final String? preferredLanguage;
  final int? householdSize;
  final int? elderlyCount;
  final bool? mobilityConcern;
  final bool? oxygenDependency;
  final String? emergencyContactName;
  final String? emergencyContactPhone;
  final String? emergencyContactRelationship;
  final String? organizationName;
  final String? orgType;
  final String? contactName;
  final String? contactPhone;
  final List<String>? skills;
  final List<String>? supportTypes;
  final List<String>? languages;
  final String? transportAccess;
  final String? availability;
  final int? credits;
  final double? trustScore;

  UserRole? get userRole {
    switch (role) {
      case 'victim':
        return UserRole.affectedUser;
      case 'volunteer':
        return UserRole.volunteer;
      case 'organization':
        return UserRole.organization;
      default:
        return null;
    }
  }

  factory AuthMeDto.fromJson(Map<String, dynamic> json) {
    List<String>? ls(String k) {
      final v = json[k];
      if (v is! List) return null;
      return v.map((e) => e.toString()).toList();
    }

    return AuthMeDto(
      role: json['role'] as String? ?? '',
      id: json['id'] as String? ?? '',
      email: json['email'] as String? ?? '',
      fullName: json['full_name'] as String?,
      phone: json['phone'] as String?,
      zoneId: json['zone_id'] as String?,
      preferredLanguage: json['preferred_language'] as String?,
      householdSize: (json['household_size'] as num?)?.toInt(),
      elderlyCount: (json['elderly_count'] as num?)?.toInt(),
      mobilityConcern: json['mobility_concern'] as bool?,
      oxygenDependency: json['oxygen_dependency'] as bool?,
      emergencyContactName: json['emergency_contact_name'] as String?,
      emergencyContactPhone: json['emergency_contact_phone'] as String?,
      emergencyContactRelationship: json['emergency_contact_relationship'] as String?,
      organizationName: json['organization_name'] as String?,
      orgType: json['org_type'] as String?,
      contactName: json['contact_name'] as String?,
      contactPhone: json['contact_phone'] as String?,
      skills: ls('skills'),
      supportTypes: ls('support_types'),
      languages: ls('languages'),
      transportAccess: json['transport_access'] as String?,
      availability: json['availability'] as String?,
      credits: (json['credits'] as num?)?.toInt(),
      trustScore: (json['trust_score'] as num?)?.toDouble(),
    );
  }
}
