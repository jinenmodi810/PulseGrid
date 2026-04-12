class IncidentDetailDto {
  const IncidentDetailDto({
    required this.incidentId,
    required this.incidentType,
    required this.severity,
    required this.peopleCount,
    required this.zoneId,
    required this.status,
    required this.priorityScore,
    required this.priorityLabel,
    required this.note,
    this.assignedHelperId,
    this.assignedHelperName,
    this.rejected = const [],
    this.etaMinutes,
    required this.routeStatus,
    required this.aiGuidance,
    this.createdAt,
    required this.elderly,
    required this.childPresent,
    required this.injury,
    required this.oxygenRequired,
    required this.shelterNeeded,
    required this.foodNeeded,
    required this.transportNeeded,
    this.preferredLanguage = '',
    this.emergencyContactName,
    this.emergencyContactPhone,
    this.emergencyContactRelationship,
    this.assignedOrganizationId,
    this.assignedOrganizationName,
    this.assignedOrganizationType,
    this.responseTier = '',
    this.volunteerCandidateAllowed = true,
    this.organizationCandidateAllowed = false,
    this.escalationRequired = false,
    this.decisionSummary = '',
    this.tierReasons = const [],
    this.rejectedOrganizations = const [],
  });

  final String incidentId;
  final String incidentType;
  final String severity;
  final int peopleCount;
  final String zoneId;
  final String status;
  final double priorityScore;
  final String priorityLabel;
  final String note;
  final String? assignedHelperId;
  final String? assignedHelperName;
  final List<RejectedCandidateDto> rejected;
  final int? etaMinutes;
  final String routeStatus;
  final String aiGuidance;
  final String? createdAt;
  final bool elderly;
  final bool childPresent;
  final bool injury;
  final bool oxygenRequired;
  final bool shelterNeeded;
  final bool foodNeeded;
  final bool transportNeeded;
  final String preferredLanguage;
  final String? emergencyContactName;
  final String? emergencyContactPhone;
  final String? emergencyContactRelationship;
  final String? assignedOrganizationId;
  final String? assignedOrganizationName;
  final String? assignedOrganizationType;
  final String responseTier;
  final bool volunteerCandidateAllowed;
  final bool organizationCandidateAllowed;
  final bool escalationRequired;
  final String decisionSummary;
  final List<TierReasonDto> tierReasons;
  final List<RejectedOrganizationDto> rejectedOrganizations;

  factory IncidentDetailDto.fromJson(Map<String, dynamic> json) {
    final rejectedRaw = json['rejected_candidates'];
    final rejected = <RejectedCandidateDto>[];
    if (rejectedRaw is List) {
      for (final item in rejectedRaw) {
        if (item is Map<String, dynamic>) {
          rejected.add(
            RejectedCandidateDto(
              volunteerId: item['volunteer_id'] as String? ?? '',
              name: item['name'] as String? ?? '',
              reason: item['reason'] as String? ?? '',
            ),
          );
        }
      }
    }
    final orgRejRaw = json['rejected_organization_candidates'];
    final orgRejected = <RejectedOrganizationDto>[];
    if (orgRejRaw is List) {
      for (final item in orgRejRaw) {
        if (item is Map<String, dynamic>) {
          orgRejected.add(
            RejectedOrganizationDto(
              organizationId: item['organization_id'] as String? ?? '',
              name: item['name'] as String? ?? '',
              reason: item['reason'] as String? ?? '',
            ),
          );
        }
      }
    }
    final trRaw = json['tier_reasons'];
    final tierReasons = <TierReasonDto>[];
    if (trRaw is List) {
      for (final item in trRaw) {
        if (item is Map<String, dynamic>) {
          tierReasons.add(
            TierReasonDto(
              code: item['code'] as String? ?? '',
              detail: item['detail'] as String? ?? '',
            ),
          );
        }
      }
    }
    final helper = json['assigned_helper'];
    String? hid;
    String? hname;
    if (helper is Map<String, dynamic>) {
      hid = helper['id'] as String?;
      hname = helper['name'] as String?;
    }
    final org = json['assigned_organization'];
    String? oid;
    String? oname;
    String? otype;
    if (org is Map<String, dynamic>) {
      oid = org['id'] as String?;
      oname = org['name'] as String?;
      otype = org['org_type'] as String?;
    }
    final ec = json['emergency_contact'];
    String? ecName;
    String? ecPhone;
    String? ecRel;
    if (ec is Map<String, dynamic>) {
      ecName = ec['name'] as String?;
      ecPhone = ec['phone'] as String?;
      ecRel = ec['relationship'] as String?;
    }
    return IncidentDetailDto(
      incidentId: json['incident_id'] as String? ?? '',
      incidentType: json['incident_type'] as String? ?? '',
      severity: json['severity'] as String? ?? 'medium',
      peopleCount: (json['people_count'] as num?)?.toInt() ?? 1,
      zoneId: json['zone_id'] as String? ?? '',
      status: json['status'] as String? ?? 'open',
      priorityScore: (json['priority_score'] as num?)?.toDouble() ?? 0,
      priorityLabel: json['priority_label'] as String? ?? 'MEDIUM',
      note: json['note'] as String? ?? '',
      assignedHelperId: hid,
      assignedHelperName: hname,
      rejected: rejected,
      etaMinutes: (json['eta_minutes'] as num?)?.toInt(),
      routeStatus: json['route_status'] as String? ?? 'pending',
      aiGuidance: json['ai_guidance'] as String? ?? '',
      createdAt: json['created_at'] as String?,
      elderly: json['elderly'] as bool? ?? false,
      childPresent: json['child_present'] as bool? ?? false,
      injury: json['injury'] as bool? ?? false,
      oxygenRequired: json['oxygen_required'] as bool? ?? false,
      shelterNeeded: json['shelter_needed'] as bool? ?? false,
      foodNeeded: json['food_needed'] as bool? ?? false,
      transportNeeded: json['transport_needed'] as bool? ?? false,
      preferredLanguage: json['preferred_language'] as String? ?? '',
      emergencyContactName: ecName,
      emergencyContactPhone: ecPhone,
      emergencyContactRelationship: ecRel,
      assignedOrganizationId: oid,
      assignedOrganizationName: oname,
      assignedOrganizationType: otype,
      responseTier: json['response_tier'] as String? ?? '',
      volunteerCandidateAllowed: json['volunteer_candidate_allowed'] as bool? ?? true,
      organizationCandidateAllowed: json['organization_candidate_allowed'] as bool? ?? false,
      escalationRequired: json['escalation_required'] as bool? ?? false,
      decisionSummary: json['decision_summary'] as String? ?? '',
      tierReasons: tierReasons,
      rejectedOrganizations: orgRejected,
    );
  }
}

class RejectedCandidateDto {
  const RejectedCandidateDto({
    required this.volunteerId,
    required this.name,
    required this.reason,
  });

  final String volunteerId;
  final String name;
  final String reason;
}

class RejectedOrganizationDto {
  const RejectedOrganizationDto({
    required this.organizationId,
    required this.name,
    required this.reason,
  });

  final String organizationId;
  final String name;
  final String reason;
}

class TierReasonDto {
  const TierReasonDto({required this.code, required this.detail});

  final String code;
  final String detail;
}
