import '../../core/enums/incident_status.dart';
import '../../core/enums/severity_level.dart';
import '../../core/utils/date_utils.dart';
import 'json_helpers.dart';

class IncidentModel {
  const IncidentModel({
    required this.id,
    required this.title,
    required this.status,
    required this.severity,
    this.createdAt,
  });

  final String id;
  final String title;
  final IncidentStatus status;
  final SeverityLevel severity;
  final DateTime? createdAt;

  factory IncidentModel.fromJson(Map<String, dynamic> json) {
    return IncidentModel(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? 'Untitled incident',
      status: enumFromName(IncidentStatus.values, json['status'] as String?, IncidentStatus.open),
      severity: enumFromName(
        SeverityLevel.values,
        json['severity'] as String?,
        SeverityLevel.medium,
      ),
      createdAt: AppDateUtils.tryParseIso(json['created_at'] as String?),
    );
  }
}
