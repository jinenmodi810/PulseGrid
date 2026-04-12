/// Payload for POST /incidents/preview-priority.
class PriorityPreviewPayload {
  const PriorityPreviewPayload({
    required this.severity,
    required this.peopleCount,
    required this.elderly,
    required this.childPresent,
    required this.injury,
    required this.oxygenRequired,
    required this.shelterNeeded,
    required this.foodNeeded,
    required this.transportNeeded,
  });

  final String severity;
  final int peopleCount;
  final bool elderly;
  final bool childPresent;
  final bool injury;
  final bool oxygenRequired;
  final bool shelterNeeded;
  final bool foodNeeded;
  final bool transportNeeded;

  Map<String, dynamic> toJson() => {
        'severity': severity,
        'people_count': peopleCount,
        'elderly': elderly,
        'child_present': childPresent,
        'injury': injury,
        'oxygen_required': oxygenRequired,
        'shelter_needed': shelterNeeded,
        'food_needed': foodNeeded,
        'transport_needed': transportNeeded,
      };
}
