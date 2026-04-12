import '../../core/enums/support_type.dart';
import 'json_helpers.dart';

class SupportContactModel {
  const SupportContactModel({
    required this.id,
    required this.label,
    required this.phone,
    required this.type,
  });

  final String id;
  final String label;
  final String phone;
  final SupportType type;

  factory SupportContactModel.fromJson(Map<String, dynamic> json) {
    return SupportContactModel(
      id: json['id'] as String? ?? '',
      label: json['label'] as String? ?? 'Support',
      phone: json['phone'] as String? ?? '',
      type: enumFromName(SupportType.values, json['type'] as String?, SupportType.other),
    );
  }
}
