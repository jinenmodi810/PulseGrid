/// Payload for POST /incidents (mirrors backend CreateIncidentRequest).
class HelpRequestSubmitPayload {
  const HelpRequestSubmitPayload({
    required this.userId,
    required this.incidentType,
    required this.severity,
    required this.peopleCount,
    required this.zoneId,
    required this.elderly,
    required this.childPresent,
    required this.injury,
    required this.oxygenRequired,
    required this.shelterNeeded,
    required this.foodNeeded,
    required this.transportNeeded,
    required this.note,
    this.useProfileForPeopleCount = true,
    this.useProfileForElderly = true,
    this.useProfileForOxygenRequired = true,
    this.intakeSource = 'form',
  });

  final String userId;
  final String incidentType;
  final String severity;
  final int peopleCount;
  final String zoneId;
  final bool elderly;
  final bool childPresent;
  final bool injury;
  final bool oxygenRequired;
  final bool shelterNeeded;
  final bool foodNeeded;
  final bool transportNeeded;
  final String note;
  final bool useProfileForPeopleCount;
  final bool useProfileForElderly;
  final bool useProfileForOxygenRequired;
  /// `form` or `voice_stub` — backend stores on incident; full voice pipeline is future work.
  final String intakeSource;

  Map<String, dynamic> toJson() => {
        'user_id': userId,
        'incident_type': incidentType,
        'severity': severity,
        'people_count': peopleCount,
        'zone_id': zoneId,
        'elderly': elderly,
        'child_present': childPresent,
        'injury': injury,
        'oxygen_required': oxygenRequired,
        'shelter_needed': shelterNeeded,
        'food_needed': foodNeeded,
        'transport_needed': transportNeeded,
        'note': note,
        'use_profile_for_people_count': useProfileForPeopleCount,
        'use_profile_for_elderly': useProfileForElderly,
        'use_profile_for_oxygen_required': useProfileForOxygenRequired,
        'intake_source': intakeSource,
      };
}
