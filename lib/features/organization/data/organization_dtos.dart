class OrganizationOverviewDto {
  const OrganizationOverviewDto({
    required this.organizationId,
    required this.name,
    required this.orgType,
    required this.zoneId,
    required this.active,
    required this.assignedIncidentsOpen,
    required this.capacity,
  });

  final String organizationId;
  final String name;
  final String orgType;
  final String zoneId;
  final bool active;
  final int assignedIncidentsOpen;
  final Map<String, dynamic> capacity;

  factory OrganizationOverviewDto.fromJson(Map<String, dynamic> json) {
    final cap = json['capacity'];
    return OrganizationOverviewDto(
      organizationId: json['organization_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      orgType: json['org_type'] as String? ?? '',
      zoneId: json['zone_id'] as String? ?? '',
      active: json['active'] as bool? ?? true,
      assignedIncidentsOpen: (json['assigned_incidents_open'] as num?)?.toInt() ?? 0,
      capacity: cap is Map<String, dynamic> ? Map<String, dynamic>.from(cap) : {},
    );
  }
}

class OrganizationIncidentRowDto {
  const OrganizationIncidentRowDto({
    required this.incidentId,
    required this.incidentType,
    required this.severity,
    required this.status,
    required this.priorityLabel,
    required this.priorityScore,
    required this.zoneId,
    required this.assignedVolunteerName,
    required this.responseTier,
    required this.escalationRequired,
    this.decisionSummary = '',
    this.volunteerSupportActive = false,
    this.createdAt,
  });

  final String incidentId;
  final String incidentType;
  final String severity;
  final String status;
  final String priorityLabel;
  final double priorityScore;
  final String zoneId;
  final String assignedVolunteerName;
  final String responseTier;
  final bool escalationRequired;
  final String decisionSummary;
  final bool volunteerSupportActive;
  final String? createdAt;

  factory OrganizationIncidentRowDto.fromJson(Map<String, dynamic> json) {
    return OrganizationIncidentRowDto(
      incidentId: json['incident_id'] as String? ?? '',
      incidentType: json['incident_type'] as String? ?? '',
      severity: json['severity'] as String? ?? 'medium',
      status: json['status'] as String? ?? 'open',
      priorityLabel: json['priority_label'] as String? ?? 'MEDIUM',
      priorityScore: (json['priority_score'] as num?)?.toDouble() ?? 0,
      zoneId: json['zone_id'] as String? ?? '',
      assignedVolunteerName: json['assigned_volunteer_name'] as String? ?? '',
      responseTier: json['response_tier'] as String? ?? '',
      escalationRequired: json['escalation_required'] as bool? ?? false,
      decisionSummary: json['decision_summary'] as String? ?? '',
      volunteerSupportActive: json['volunteer_support_active'] as bool? ?? false,
      createdAt: json['created_at'] as String?,
    );
  }
}
