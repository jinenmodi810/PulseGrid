/// Canonical support_type values stored on Volunteer.support_types (Neo4j).
const List<String> kVolunteerSupportTypeIds = [
  'medical',
  'transport',
  'food',
  'shelter',
  'elderly_support',
  'child_support',
  'general_support',
];

String supportTypeLabel(String id) {
  switch (id) {
    case 'medical':
      return 'Medical';
    case 'transport':
      return 'Transport';
    case 'food':
      return 'Food';
    case 'shelter':
      return 'Shelter';
    case 'elderly_support':
      return 'Elderly support';
    case 'child_support':
      return 'Child support';
    case 'general_support':
      return 'General';
    default:
      return id;
  }
}

/// Practical skill tags (also stored in Volunteer.skills).
const List<String> kVolunteerSkillChipIds = [
  'medical',
  'logistics',
  'communications',
  'search_rescue',
  'mental_health',
  'general',
];

String skillChipLabel(String id) {
  const m = <String, String>{
    'medical': 'Medical',
    'logistics': 'Logistics',
    'communications': 'Communications',
    'search_rescue': 'Search & rescue',
    'mental_health': 'Mental health',
    'general': 'General',
  };
  return m[id] ?? (id.isEmpty ? id : '${id[0].toUpperCase()}${id.substring(1)}');
}
