import '../../../app/constants/app_constants.dart';
import '../../../core/enums/user_role.dart';
import '../../../core/services/storage_service.dart';

/// Persists lightweight session flags for role-based routing.
class SessionStore {
  SessionStore(this._storage);

  final StorageService _storage;

  Future<void> setAuthToken(String? token) async {
    if (token != null && token.isNotEmpty) {
      await _storage.setString(SessionKeys.authToken, token);
    } else {
      await _storage.remove(SessionKeys.authToken);
    }
  }

  Future<String?> getAuthToken() => _storage.getString(SessionKeys.authToken);

  Future<void> saveAffectedUser({
    required String userId,
    required String zoneId,
    String? accessToken,
    int? householdSize,
    int? elderlyCount,
    bool? oxygenDependency,
    String? preferredLanguage,
    bool? mobilityConcern,
  }) async {
    await _storage.setString(SessionKeys.role, UserRole.affectedUser.name);
    await _storage.setString(SessionKeys.graphUserId, userId);
    await _storage.setString(SessionKeys.zoneId, zoneId);
    if (accessToken != null && accessToken.isNotEmpty) {
      await _storage.setString(SessionKeys.authToken, accessToken);
    }
    await _storage.remove(SessionKeys.graphVolunteerId);
    await _storage.remove(SessionKeys.graphOrganizationId);
    await _storage.remove(SessionKeys.organizationType);
    await _storage.remove(SessionKeys.volunteerAvailability);
    if (householdSize != null) {
      await _storage.setString(SessionKeys.userHouseholdSize, '$householdSize');
    } else {
      await _storage.remove(SessionKeys.userHouseholdSize);
    }
    if (elderlyCount != null) {
      await _storage.setString(SessionKeys.userElderlyCount, '$elderlyCount');
    } else {
      await _storage.remove(SessionKeys.userElderlyCount);
    }
    if (oxygenDependency != null) {
      await _storage.setString(SessionKeys.userOxygenDependency, oxygenDependency ? '1' : '0');
    } else {
      await _storage.remove(SessionKeys.userOxygenDependency);
    }
    if (preferredLanguage != null && preferredLanguage.isNotEmpty) {
      await _storage.setString(SessionKeys.userPreferredLanguage, preferredLanguage);
    } else {
      await _storage.remove(SessionKeys.userPreferredLanguage);
    }
    if (mobilityConcern != null) {
      await _storage.setString(SessionKeys.userMobilityConcern, mobilityConcern ? '1' : '0');
    } else {
      await _storage.remove(SessionKeys.userMobilityConcern);
    }
  }

  Future<void> saveVolunteer({
    required String volunteerId,
    required String zoneId,
    String? accessToken,
    String? availability,
  }) async {
    await _storage.setString(SessionKeys.role, UserRole.volunteer.name);
    await _storage.setString(SessionKeys.graphVolunteerId, volunteerId);
    await _storage.setString(SessionKeys.zoneId, zoneId);
    if (accessToken != null && accessToken.isNotEmpty) {
      await _storage.setString(SessionKeys.authToken, accessToken);
    }
    if (availability != null && availability.isNotEmpty) {
      await _storage.setString(SessionKeys.volunteerAvailability, availability);
    } else {
      await _storage.remove(SessionKeys.volunteerAvailability);
    }
    await _storage.remove(SessionKeys.graphUserId);
    await _storage.remove(SessionKeys.graphOrganizationId);
    await _storage.remove(SessionKeys.organizationType);
    await _storage.remove(SessionKeys.userHouseholdSize);
    await _storage.remove(SessionKeys.userElderlyCount);
    await _storage.remove(SessionKeys.userOxygenDependency);
    await _storage.remove(SessionKeys.userPreferredLanguage);
    await _storage.remove(SessionKeys.userMobilityConcern);
  }

  Future<void> saveOrganization({
    required String organizationId,
    required String zoneId,
    String? accessToken,
    String? organizationType,
  }) async {
    await _storage.setString(SessionKeys.role, UserRole.organization.name);
    await _storage.setString(SessionKeys.graphOrganizationId, organizationId);
    await _storage.setString(SessionKeys.zoneId, zoneId);
    if (accessToken != null && accessToken.isNotEmpty) {
      await _storage.setString(SessionKeys.authToken, accessToken);
    }
    if (organizationType != null && organizationType.isNotEmpty) {
      await _storage.setString(SessionKeys.organizationType, organizationType);
    } else {
      await _storage.remove(SessionKeys.organizationType);
    }
    await _storage.remove(SessionKeys.graphUserId);
    await _storage.remove(SessionKeys.graphVolunteerId);
    await _storage.remove(SessionKeys.volunteerAvailability);
    await _storage.remove(SessionKeys.userHouseholdSize);
    await _storage.remove(SessionKeys.userElderlyCount);
    await _storage.remove(SessionKeys.userOxygenDependency);
    await _storage.remove(SessionKeys.userPreferredLanguage);
    await _storage.remove(SessionKeys.userMobilityConcern);
  }

  Future<void> clearSession() async {
    await _storage.remove(SessionKeys.authToken);
    await _storage.remove(SessionKeys.role);
    await _storage.remove(SessionKeys.graphUserId);
    await _storage.remove(SessionKeys.graphVolunteerId);
    await _storage.remove(SessionKeys.graphOrganizationId);
    await _storage.remove(SessionKeys.zoneId);
    await _storage.remove(SessionKeys.organizationType);
    await _storage.remove(SessionKeys.volunteerAvailability);
    await _storage.remove(SessionKeys.userHouseholdSize);
    await _storage.remove(SessionKeys.userElderlyCount);
    await _storage.remove(SessionKeys.userOxygenDependency);
    await _storage.remove(SessionKeys.userPreferredLanguage);
    await _storage.remove(SessionKeys.userMobilityConcern);
    await _storage.remove(SessionKeys.lastIncidentId);
  }

  Future<UserRole?> readRole() async {
    final raw = await _storage.getString(SessionKeys.role);
    if (raw == null) {
      return null;
    }
    for (final role in UserRole.values) {
      if (role.name == raw) {
        return role;
      }
    }
    return null;
  }
}
