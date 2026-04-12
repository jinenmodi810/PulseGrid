import '../../core/enums/incident_status.dart';
import '../../core/enums/severity_level.dart';

/// Domain representation of an incident.
///
/// TODO(Phase1): map from [IncidentModel] at the repository boundary.
class IncidentEntity {
  const IncidentEntity({
    required this.id,
    required this.title,
    required this.status,
    required this.severity,
  });

  final String id;
  final String title;
  final IncidentStatus status;
  final SeverityLevel severity;
}
