class RegisterOrganizationPayload {
  const RegisterOrganizationPayload({
    required this.organizationName,
    required this.organizationType,
    required this.contactName,
    required this.contactPhone,
    required this.contactEmail,
    required this.password,
    required this.zoneId,
    this.coverageZoneIds = const [],
    this.bedsAvailable,
    this.oxygenUnits,
    this.ambulancesAvailable,
    this.shelterUnits,
    this.foodCapacityUnits,
    this.rescueUnits,
  });

  final String organizationName;
  final String organizationType;
  final String contactName;
  final String contactPhone;
  final String contactEmail;
  final String password;
  final String zoneId;
  final List<String> coverageZoneIds;
  final int? bedsAvailable;
  final int? oxygenUnits;
  final int? ambulancesAvailable;
  final int? shelterUnits;
  final int? foodCapacityUnits;
  final int? rescueUnits;

  Map<String, dynamic> toJson() => {
        'organization_name': organizationName,
        'organization_type': organizationType,
        'contact_name': contactName,
        'contact_phone': contactPhone,
        'contact_email': contactEmail,
        'password': password,
        'zone_id': zoneId,
        'coverage_zone_ids': coverageZoneIds,
        if (bedsAvailable != null) 'beds_available': bedsAvailable,
        if (oxygenUnits != null) 'oxygen_units': oxygenUnits,
        if (ambulancesAvailable != null) 'ambulances_available': ambulancesAvailable,
        if (shelterUnits != null) 'shelter_units': shelterUnits,
        if (foodCapacityUnits != null) 'food_capacity_units': foodCapacityUnits,
        if (rescueUnits != null) 'rescue_units': rescueUnits,
      };
}
