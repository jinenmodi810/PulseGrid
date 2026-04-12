/// Outcome of assigning a destination or helper to an incident.
class AssignmentResultModel {
  const AssignmentResultModel({
    required this.incidentId,
    required this.assignedResourceId,
    required this.accepted,
    this.rejectionReasons = const [],
  });

  final String incidentId;
  final String assignedResourceId;
  final bool accepted;
  final List<String> rejectionReasons;

  factory AssignmentResultModel.fromJson(Map<String, dynamic> json) {
    final reasonsRaw = json['rejection_reasons'];
    final reasons = <String>[];
    if (reasonsRaw is List) {
      for (final item in reasonsRaw) {
        if (item is String) {
          reasons.add(item);
        }
      }
    }
    return AssignmentResultModel(
      incidentId: json['incident_id'] as String? ?? '',
      assignedResourceId: json['assigned_resource_id'] as String? ?? '',
      accepted: json['accepted'] as bool? ?? false,
      rejectionReasons: reasons,
    );
  }
}
