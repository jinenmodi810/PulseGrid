/// Demo zone ids aligned with backend seed (`zones.json`).
const List<String> kAuthZoneIds = [
  'zone-riverside',
  'zone-central',
  'zone-north',
  'zone-east',
];

/// Short labels for chip UI (ids stay canonical for Neo4j).
const Map<String, String> kAuthZoneLabels = {
  'zone-riverside': 'Riverside',
  'zone-central': 'Central',
  'zone-north': 'North',
  'zone-east': 'East',
};

String zoneLabel(String zoneId) => kAuthZoneLabels[zoneId] ?? zoneId;
