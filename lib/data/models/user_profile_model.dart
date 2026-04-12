import '../../core/enums/user_role.dart';
import 'json_helpers.dart';

class UserProfileModel {
  const UserProfileModel({
    required this.id,
    required this.displayName,
    required this.role,
    required this.trustScore,
  });

  final String id;
  final String displayName;
  final UserRole role;
  final double trustScore;

  factory UserProfileModel.fromJson(Map<String, dynamic> json) {
    return UserProfileModel(
      id: json['id'] as String? ?? 'local-user',
      displayName: json['display_name'] as String? ?? 'Community member',
      role: enumFromName(UserRole.values, json['role'] as String?, UserRole.affectedUser),
      trustScore: (json['trust_score'] as num?)?.toDouble() ?? 0,
    );
  }

  /// Local placeholder when no remote profile is wired for this surface.
  factory UserProfileModel.placeholder() {
    return const UserProfileModel(
      id: 'local-user',
      displayName: 'Community member',
      role: UserRole.affectedUser,
      trustScore: 0.6,
    );
  }
}
