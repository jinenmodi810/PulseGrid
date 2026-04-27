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

class AnalyticsOverviewDto {
  const AnalyticsOverviewDto({
    required this.incidentsTotal,
    required this.avgTimeToAssignmentSeconds,
    required this.avgTimeToCompletionSeconds,
    required this.bedsAvailableTotal,
    required this.tasksCompletedTotal,
  });

  final int incidentsTotal;
  final double? avgTimeToAssignmentSeconds;
  final double? avgTimeToCompletionSeconds;
  final int? bedsAvailableTotal;
  final int? tasksCompletedTotal;

  factory AnalyticsOverviewDto.fromJson(Map<String, dynamic> json) {
    final incidentOps = (json['incident_operations'] as Map?)?.cast<String, dynamic>() ?? const {};
    final volunteerOps = (json['volunteer_performance'] as Map?)?.cast<String, dynamic>() ?? const {};
    final orgOps = (json['organization_capacity'] as Map?)?.cast<String, dynamic>() ?? const {};
    return AnalyticsOverviewDto(
      incidentsTotal: (incidentOps['incidents_total'] as num?)?.toInt() ?? 0,
      avgTimeToAssignmentSeconds: (incidentOps['avg_time_to_assignment_seconds'] as num?)?.toDouble(),
      avgTimeToCompletionSeconds: (incidentOps['avg_time_to_completion_seconds'] as num?)?.toDouble(),
      bedsAvailableTotal: (orgOps['beds_available_total'] as num?)?.toInt(),
      tasksCompletedTotal: (volunteerOps['tasks_completed_total'] as num?)?.toInt(),
    );
  }
}

class IncidentsByZoneDto {
  const IncidentsByZoneDto({
    required this.zoneId,
    required this.incidents,
  });

  final String zoneId;
  final int incidents;

  factory IncidentsByZoneDto.fromJson(Map<String, dynamic> json) {
    return IncidentsByZoneDto(
      zoneId: json['zone_id'] as String? ?? '',
      incidents: (json['incidents'] as num?)?.toInt() ?? 0,
    );
  }
}

class TimeToResponseDto {
  const TimeToResponseDto({
    this.avgTimeToAssignmentSeconds,
    this.avgTimeToAcceptanceSeconds,
    this.avgTimeToCompletionSeconds,
  });

  final double? avgTimeToAssignmentSeconds;
  final double? avgTimeToAcceptanceSeconds;
  final double? avgTimeToCompletionSeconds;

  factory TimeToResponseDto.fromJson(Map<String, dynamic> json) {
    return TimeToResponseDto(
      avgTimeToAssignmentSeconds: (json['avg_time_to_assignment_seconds'] as num?)?.toDouble(),
      avgTimeToAcceptanceSeconds: (json['avg_time_to_acceptance_seconds'] as num?)?.toDouble(),
      avgTimeToCompletionSeconds: (json['avg_time_to_completion_seconds'] as num?)?.toDouble(),
    );
  }
}

class OrganizationCapacityAnalyticsDto {
  const OrganizationCapacityAnalyticsDto({
    required this.organizationId,
    this.capturedAt,
    this.bedsAvailable,
    this.oxygenUnits,
    this.ambulancesAvailable,
    this.shelterUnits,
    this.foodCapacityUnits,
    this.rescueUnits,
  });

  final String organizationId;
  final String? capturedAt;
  final int? bedsAvailable;
  final int? oxygenUnits;
  final int? ambulancesAvailable;
  final int? shelterUnits;
  final int? foodCapacityUnits;
  final int? rescueUnits;

  factory OrganizationCapacityAnalyticsDto.fromJson(Map<String, dynamic> json) {
    return OrganizationCapacityAnalyticsDto(
      organizationId: json['organization_id'] as String? ?? '',
      capturedAt: json['captured_at'] as String?,
      bedsAvailable: (json['beds_available'] as num?)?.toInt(),
      oxygenUnits: (json['oxygen_units'] as num?)?.toInt(),
      ambulancesAvailable: (json['ambulances_available'] as num?)?.toInt(),
      shelterUnits: (json['shelter_units'] as num?)?.toInt(),
      foodCapacityUnits: (json['food_capacity_units'] as num?)?.toInt(),
      rescueUnits: (json['rescue_units'] as num?)?.toInt(),
    );
  }
}
