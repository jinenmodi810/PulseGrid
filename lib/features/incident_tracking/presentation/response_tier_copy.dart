/// User-facing labels for deterministic backend `response_tier` values.
String responseTierHeadline(String tier) {
  switch (tier) {
    case 'volunteer_only':
      return 'Volunteer-led';
    case 'organization_only':
      return 'Organization-led';
    case 'volunteer_plus_organization':
      return 'Volunteer + organization';
    case 'escalation_required':
      return 'Escalation required';
    default:
      return 'Routing';
  }
}
