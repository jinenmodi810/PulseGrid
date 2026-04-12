// DTOs for admin inspection API (snake_case JSON → typed Dart).

class AdminOverviewDto {
  const AdminOverviewDto({
    required this.totalUsers,
    required this.totalVolunteers,
    required this.totalIncidents,
    required this.activeIncidents,
    required this.pendingIncidents,
    required this.acceptedIncidents,
    required this.resolvedIncidents,
    required this.totalHospitals,
    required this.totalShelters,
    required this.totalSupportContacts,
    required this.totalZones,
    required this.totalRewards,
    required this.totalAssignedIncidents,
    required this.totalCompletedIncidents,
    required this.averageVolunteerTrustScore,
    required this.totalVolunteerCredits,
  });

  final int totalUsers;
  final int totalVolunteers;
  final int totalIncidents;
  final int activeIncidents;
  final int pendingIncidents;
  final int acceptedIncidents;
  final int resolvedIncidents;
  final int totalHospitals;
  final int totalShelters;
  final int totalSupportContacts;
  final int totalZones;
  final int totalRewards;
  final int totalAssignedIncidents;
  final int totalCompletedIncidents;
  final double averageVolunteerTrustScore;
  final int totalVolunteerCredits;

  factory AdminOverviewDto.fromJson(Map<String, dynamic> json) {
    return AdminOverviewDto(
      totalUsers: (json['total_users'] as num?)?.toInt() ?? 0,
      totalVolunteers: (json['total_volunteers'] as num?)?.toInt() ?? 0,
      totalIncidents: (json['total_incidents'] as num?)?.toInt() ?? 0,
      activeIncidents: (json['active_incidents'] as num?)?.toInt() ?? 0,
      pendingIncidents: (json['pending_incidents'] as num?)?.toInt() ?? 0,
      acceptedIncidents: (json['accepted_incidents'] as num?)?.toInt() ?? 0,
      resolvedIncidents: (json['resolved_incidents'] as num?)?.toInt() ?? 0,
      totalHospitals: (json['total_hospitals'] as num?)?.toInt() ?? 0,
      totalShelters: (json['total_shelters'] as num?)?.toInt() ?? 0,
      totalSupportContacts: (json['total_support_contacts'] as num?)?.toInt() ?? 0,
      totalZones: (json['total_zones'] as num?)?.toInt() ?? 0,
      totalRewards: (json['total_rewards'] as num?)?.toInt() ?? 0,
      totalAssignedIncidents: (json['total_assigned_incidents'] as num?)?.toInt() ?? 0,
      totalCompletedIncidents: (json['total_completed_incidents'] as num?)?.toInt() ?? 0,
      averageVolunteerTrustScore: (json['average_volunteer_trust_score'] as num?)?.toDouble() ?? 0,
      totalVolunteerCredits: (json['total_volunteer_credits'] as num?)?.toInt() ?? 0,
    );
  }
}

class AdminUserDto {
  const AdminUserDto({
    required this.userId,
    required this.name,
    required this.phone,
    required this.language,
    required this.zoneId,
    this.familySize,
    this.createdAt,
  });

  final String userId;
  final String name;
  final String phone;
  final String language;
  final String zoneId;
  final int? familySize;
  final String? createdAt;

  factory AdminUserDto.fromJson(Map<String, dynamic> json) {
    return AdminUserDto(
      userId: json['user_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      phone: json['phone'] as String? ?? '',
      language: json['language'] as String? ?? '',
      zoneId: json['zone_id'] as String? ?? '',
      familySize: (json['family_size'] as num?)?.toInt(),
      createdAt: json['created_at'] as String?,
    );
  }
}

class AdminVolunteerDto {
  const AdminVolunteerDto({
    required this.volunteerId,
    required this.name,
    required this.phone,
    required this.skillType,
    required this.languages,
    required this.zoneId,
    required this.availability,
    required this.verified,
    required this.trustScore,
    required this.credits,
    required this.assignedIncidentCount,
    required this.completedIncidentCount,
  });

  final String volunteerId;
  final String name;
  final String phone;
  final String skillType;
  final List<String> languages;
  final String zoneId;
  final String availability;
  final bool verified;
  final double trustScore;
  final int credits;
  final int assignedIncidentCount;
  final int completedIncidentCount;

  factory AdminVolunteerDto.fromJson(Map<String, dynamic> json) {
    final langs = json['languages'];
    return AdminVolunteerDto(
      volunteerId: json['volunteer_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      phone: json['phone'] as String? ?? '',
      skillType: json['skill_type'] as String? ?? '',
      languages: langs is List ? langs.map((e) => e.toString()).toList() : const [],
      zoneId: json['zone_id'] as String? ?? '',
      availability: json['availability'] as String? ?? '',
      verified: json['verified'] as bool? ?? false,
      trustScore: (json['trust_score'] as num?)?.toDouble() ?? 0,
      credits: (json['credits'] as num?)?.toInt() ?? 0,
      assignedIncidentCount: (json['assigned_incident_count'] as num?)?.toInt() ?? 0,
      completedIncidentCount: (json['completed_incident_count'] as num?)?.toInt() ?? 0,
    );
  }
}

class AdminIncidentDto {
  const AdminIncidentDto({
    required this.incidentId,
    required this.incidentType,
    required this.severity,
    required this.priorityScore,
    required this.priorityLabel,
    required this.status,
    required this.zoneId,
    required this.peopleCount,
    this.createdAt,
    this.reportedByUserId,
    this.assignedVolunteerId,
    required this.elderly,
    required this.childPresent,
    required this.injury,
    required this.oxygenRequired,
    required this.shelterNeeded,
    required this.foodNeeded,
    required this.transportNeeded,
    required this.note,
  });

  final String incidentId;
  final String incidentType;
  final String severity;
  final double priorityScore;
  final String priorityLabel;
  final String status;
  final String zoneId;
  final int peopleCount;
  final String? createdAt;
  final String? reportedByUserId;
  final String? assignedVolunteerId;
  final bool elderly;
  final bool childPresent;
  final bool injury;
  final bool oxygenRequired;
  final bool shelterNeeded;
  final bool foodNeeded;
  final bool transportNeeded;
  final String note;

  factory AdminIncidentDto.fromJson(Map<String, dynamic> json) {
    return AdminIncidentDto(
      incidentId: json['incident_id'] as String? ?? '',
      incidentType: json['incident_type'] as String? ?? '',
      severity: json['severity'] as String? ?? '',
      priorityScore: (json['priority_score'] as num?)?.toDouble() ?? 0,
      priorityLabel: json['priority_label'] as String? ?? '',
      status: json['status'] as String? ?? '',
      zoneId: json['zone_id'] as String? ?? '',
      peopleCount: (json['people_count'] as num?)?.toInt() ?? 1,
      createdAt: json['created_at'] as String?,
      reportedByUserId: json['reported_by_user_id'] as String?,
      assignedVolunteerId: json['assigned_volunteer_id'] as String?,
      elderly: json['elderly'] as bool? ?? false,
      childPresent: json['child_present'] as bool? ?? false,
      injury: json['injury'] as bool? ?? false,
      oxygenRequired: json['oxygen_required'] as bool? ?? false,
      shelterNeeded: json['shelter_needed'] as bool? ?? false,
      foodNeeded: json['food_needed'] as bool? ?? false,
      transportNeeded: json['transport_needed'] as bool? ?? false,
      note: json['note'] as String? ?? '',
    );
  }
}

class AdminIncidentReporterDto {
  const AdminIncidentReporterDto({
    required this.userId,
    required this.name,
    required this.phone,
    required this.zoneId,
  });

  final String userId;
  final String name;
  final String phone;
  final String zoneId;

  factory AdminIncidentReporterDto.fromJson(Map<String, dynamic>? json) {
    if (json == null) {
      return const AdminIncidentReporterDto(userId: '', name: '', phone: '', zoneId: '');
    }
    return AdminIncidentReporterDto(
      userId: json['user_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      phone: json['phone'] as String? ?? '',
      zoneId: json['zone_id'] as String? ?? '',
    );
  }
}

class AdminIncidentVolunteerDto {
  const AdminIncidentVolunteerDto({
    required this.volunteerId,
    required this.name,
    required this.phone,
  });

  final String volunteerId;
  final String name;
  final String phone;

  factory AdminIncidentVolunteerDto.fromJson(Map<String, dynamic>? json) {
    if (json == null) {
      return const AdminIncidentVolunteerDto(volunteerId: '', name: '', phone: '');
    }
    return AdminIncidentVolunteerDto(
      volunteerId: json['volunteer_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      phone: json['phone'] as String? ?? '',
    );
  }
}

class AdminIncidentZoneDto {
  const AdminIncidentZoneDto({required this.zoneId, required this.name});

  final String zoneId;
  final String name;

  factory AdminIncidentZoneDto.fromJson(Map<String, dynamic>? json) {
    if (json == null) {
      return const AdminIncidentZoneDto(zoneId: '', name: '');
    }
    return AdminIncidentZoneDto(
      zoneId: json['zone_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
    );
  }
}

class AdminRejectedDto {
  const AdminRejectedDto({required this.volunteerId, required this.name, required this.reason});

  final String volunteerId;
  final String name;
  final String reason;

  factory AdminRejectedDto.fromJson(Map<String, dynamic> json) {
    return AdminRejectedDto(
      volunteerId: json['volunteer_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      reason: json['reason'] as String? ?? '',
    );
  }
}

class AdminIncidentDetailDto {
  const AdminIncidentDetailDto({
    required this.incident,
    this.reportingUser,
    this.assignedVolunteer,
    this.zone,
    required this.routeStatus,
    required this.aiGuidance,
    required this.rejectedCandidates,
    required this.statusHistory,
    required this.relationshipsSummary,
  });

  final AdminIncidentDto incident;
  final AdminIncidentReporterDto? reportingUser;
  final AdminIncidentVolunteerDto? assignedVolunteer;
  final AdminIncidentZoneDto? zone;
  final String routeStatus;
  final String aiGuidance;
  final List<AdminRejectedDto> rejectedCandidates;
  final List<Map<String, dynamic>> statusHistory;
  final String relationshipsSummary;

  factory AdminIncidentDetailDto.fromJson(Map<String, dynamic> json) {
    final hist = json['status_history'];
    return AdminIncidentDetailDto(
      incident: AdminIncidentDto.fromJson(json['incident'] as Map<String, dynamic>? ?? {}),
      reportingUser: json['reporting_user'] != null
          ? AdminIncidentReporterDto.fromJson(json['reporting_user'] as Map<String, dynamic>)
          : null,
      assignedVolunteer: json['assigned_volunteer'] != null
          ? AdminIncidentVolunteerDto.fromJson(json['assigned_volunteer'] as Map<String, dynamic>)
          : null,
      zone: json['zone'] != null ? AdminIncidentZoneDto.fromJson(json['zone'] as Map<String, dynamic>) : null,
      routeStatus: json['route_status'] as String? ?? '',
      aiGuidance: json['ai_guidance'] as String? ?? '',
      rejectedCandidates: (json['rejected_candidates'] as List<dynamic>?)
              ?.whereType<Map<String, dynamic>>()
              .map(AdminRejectedDto.fromJson)
              .toList() ??
          const [],
      statusHistory: (hist as List<dynamic>?)?.map((e) => Map<String, dynamic>.from(e as Map)).toList() ?? const [],
      relationshipsSummary: json['relationships_summary'] as String? ?? '',
    );
  }
}

class AdminAssignmentDto {
  const AdminAssignmentDto({
    required this.incidentId,
    required this.volunteerId,
    required this.volunteerName,
    required this.status,
    required this.zoneId,
    required this.priorityLabel,
    this.assignedAt,
  });

  final String incidentId;
  final String volunteerId;
  final String volunteerName;
  final String status;
  final String zoneId;
  final String priorityLabel;
  final String? assignedAt;

  factory AdminAssignmentDto.fromJson(Map<String, dynamic> json) {
    return AdminAssignmentDto(
      incidentId: json['incident_id'] as String? ?? '',
      volunteerId: json['volunteer_id'] as String? ?? '',
      volunteerName: json['volunteer_name'] as String? ?? '',
      status: json['status'] as String? ?? '',
      zoneId: json['zone_id'] as String? ?? '',
      priorityLabel: json['priority_label'] as String? ?? '',
      assignedAt: json['assigned_at'] as String?,
    );
  }
}

class AdminRewardDto {
  const AdminRewardDto({
    required this.volunteerId,
    required this.volunteerName,
    required this.credits,
    required this.trustScore,
    required this.earnedRewardCount,
    required this.completedIncidentCount,
  });

  final String volunteerId;
  final String volunteerName;
  final int credits;
  final double trustScore;
  final int earnedRewardCount;
  final int completedIncidentCount;

  factory AdminRewardDto.fromJson(Map<String, dynamic> json) {
    return AdminRewardDto(
      volunteerId: json['volunteer_id'] as String? ?? '',
      volunteerName: json['volunteer_name'] as String? ?? '',
      credits: (json['credits'] as num?)?.toInt() ?? 0,
      trustScore: (json['trust_score'] as num?)?.toDouble() ?? 0,
      earnedRewardCount: (json['earned_reward_count'] as num?)?.toInt() ?? 0,
      completedIncidentCount: (json['completed_incident_count'] as num?)?.toInt() ?? 0,
    );
  }
}

class AdminSupportNetworkDto {
  const AdminSupportNetworkDto({
    required this.hospitals,
    required this.shelters,
    required this.supportContacts,
    required this.zones,
  });

  final List<Map<String, dynamic>> hospitals;
  final List<Map<String, dynamic>> shelters;
  final List<Map<String, dynamic>> supportContacts;
  final List<Map<String, dynamic>> zones;

  factory AdminSupportNetworkDto.fromJson(Map<String, dynamic> json) {
    List<Map<String, dynamic>> asMapList(String key) {
      final raw = json[key] as List<dynamic>?;
      if (raw == null) {
        return const [];
      }
      return raw.map((e) => Map<String, dynamic>.from(e as Map)).toList();
    }

    return AdminSupportNetworkDto(
      hospitals: asMapList('hospitals'),
      shelters: asMapList('shelters'),
      supportContacts: asMapList('support_contacts'),
      zones: asMapList('zones'),
    );
  }
}
