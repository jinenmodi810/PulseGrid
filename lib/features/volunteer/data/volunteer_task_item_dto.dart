class VolunteerTaskItemDto {
  const VolunteerTaskItemDto({
    required this.incidentId,
    required this.incidentType,
    required this.priorityLabel,
    required this.priorityScore,
    required this.zoneId,
    required this.status,
    required this.note,
    this.etaMinutes,
    required this.routeStatus,
    required this.shelterNeeded,
    required this.foodNeeded,
    required this.transportNeeded,
    required this.elderly,
    required this.childPresent,
    required this.injury,
    required this.oxygenRequired,
    required this.taskSource,
    this.responseTier = '',
    this.decisionSummary = '',
  });

  final String incidentId;
  final String incidentType;
  final String priorityLabel;
  final double priorityScore;
  final String zoneId;
  final String status;
  final String note;
  final int? etaMinutes;
  final String routeStatus;
  final bool shelterNeeded;
  final bool foodNeeded;
  final bool transportNeeded;
  final bool elderly;
  final bool childPresent;
  final bool injury;
  final bool oxygenRequired;
  final String taskSource;
  final String responseTier;
  final String decisionSummary;

  String get summaryLine {
    if (note.isNotEmpty) return note.length > 80 ? '${note.substring(0, 80)}…' : note;
    return incidentType;
  }

  factory VolunteerTaskItemDto.fromJson(Map<String, dynamic> json) {
    return VolunteerTaskItemDto(
      incidentId: json['incident_id'] as String? ?? '',
      incidentType: json['incident_type'] as String? ?? '',
      priorityLabel: json['priority_label'] as String? ?? 'MEDIUM',
      priorityScore: (json['priority_score'] as num?)?.toDouble() ?? 0,
      zoneId: json['zone_id'] as String? ?? '',
      status: json['status'] as String? ?? 'open',
      note: json['note'] as String? ?? '',
      etaMinutes: (json['eta_minutes'] as num?)?.toInt(),
      routeStatus: json['route_status'] as String? ?? 'pending',
      shelterNeeded: json['shelter_needed'] as bool? ?? false,
      foodNeeded: json['food_needed'] as bool? ?? false,
      transportNeeded: json['transport_needed'] as bool? ?? false,
      elderly: json['elderly'] as bool? ?? false,
      childPresent: json['child_present'] as bool? ?? false,
      injury: json['injury'] as bool? ?? false,
      oxygenRequired: json['oxygen_required'] as bool? ?? false,
      taskSource: json['task_source'] as String? ?? 'assigned',
      responseTier: json['response_tier'] as String? ?? '',
      decisionSummary: json['decision_summary'] as String? ?? '',
    );
  }
}

class VolunteerProfileDto {
  const VolunteerProfileDto({
    required this.id,
    required this.displayName,
    required this.credits,
    required this.trustScore,
    this.skills = const [],
    this.zoneId = '',
    this.supportTypes = const [],
    this.languages = const [],
    this.transportAccess = '',
    this.availability = '',
  });

  final String id;
  final String displayName;
  final int credits;
  final double trustScore;
  final List<String> skills;
  final String zoneId;
  final List<String> supportTypes;
  final List<String> languages;
  final String transportAccess;
  final String availability;

  factory VolunteerProfileDto.fromJson(Map<String, dynamic> json) {
    final skillsRaw = json['skills'];
    final skills = <String>[];
    if (skillsRaw is List) {
      for (final s in skillsRaw) {
        if (s != null) skills.add(s.toString());
      }
    }
    List<String> listField(String key) {
      final raw = json[key];
      if (raw is! List) return [];
      return raw.map((e) => e.toString()).where((s) => s.isNotEmpty).toList();
    }

    return VolunteerProfileDto(
      id: json['id'] as String? ?? '',
      displayName: json['display_name'] as String? ?? '',
      credits: (json['credits'] as num?)?.toInt() ?? 0,
      trustScore: (json['trust_score'] as num?)?.toDouble() ?? 0.5,
      skills: skills,
      zoneId: json['zone_id'] as String? ?? '',
      supportTypes: listField('support_types'),
      languages: listField('languages'),
      transportAccess: json['transport_access'] as String? ?? '',
      availability: json['availability'] as String? ?? '',
    );
  }
}

class AcceptTaskResultDto {
  const AcceptTaskResultDto({
    required this.incidentId,
    required this.status,
    required this.priorityLabel,
    required this.zoneId,
  });

  final String incidentId;
  final String status;
  final String priorityLabel;
  final String zoneId;

  factory AcceptTaskResultDto.fromJson(Map<String, dynamic> json) {
    return AcceptTaskResultDto(
      incidentId: json['incident_id'] as String? ?? '',
      status: json['status'] as String? ?? '',
      priorityLabel: json['priority_label'] as String? ?? '',
      zoneId: json['zone_id'] as String? ?? '',
    );
  }
}

class CompleteTaskResultDto {
  const CompleteTaskResultDto({
    required this.incidentId,
    required this.status,
    required this.volunteerCredits,
    required this.volunteerTrustScore,
  });

  final String incidentId;
  final String status;
  final int volunteerCredits;
  final double volunteerTrustScore;

  factory CompleteTaskResultDto.fromJson(Map<String, dynamic> json) {
    final v = json['volunteer'];
    Map<String, dynamic>? vm;
    if (v is Map<String, dynamic>) vm = v;
    return CompleteTaskResultDto(
      incidentId: json['incident_id'] as String? ?? '',
      status: json['status'] as String? ?? '',
      volunteerCredits: (vm?['credits'] as num?)?.toInt() ?? 0,
      volunteerTrustScore: (vm?['trust_score'] as num?)?.toDouble() ?? 0.5,
    );
  }
}
