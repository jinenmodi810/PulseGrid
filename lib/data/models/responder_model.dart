import '../../core/enums/user_role.dart';
import 'json_helpers.dart';

class ResponderModel {
  const ResponderModel({
    required this.id,
    required this.unitName,
    required this.role,
    required this.status,
  });

  final String id;
  final String unitName;
  final UserRole role;
  final String status;

  factory ResponderModel.fromJson(Map<String, dynamic> json) {
    return ResponderModel(
      id: json['id'] as String? ?? '',
      unitName: json['unit_name'] as String? ?? 'Unit',
      role: enumFromName(UserRole.values, json['role'] as String?, UserRole.volunteer),
      status: json['status'] as String? ?? 'unknown',
    );
  }
}
