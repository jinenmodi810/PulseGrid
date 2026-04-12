import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/enums/user_role.dart';
import '../features/auth/domain/auth_me_dto.dart';
import 'constants/app_constants.dart';

/// Cold-start route from persisted session only (no network).
String resolveStartupLocation(SharedPreferences prefs) {
  final roleRaw = prefs.getString(SessionKeys.role);
  if (roleRaw == null || roleRaw.isEmpty) {
    return AppRoutes.landing;
  }
  UserRole? role;
  for (final r in UserRole.values) {
    if (r.name == roleRaw) {
      role = r;
      break;
    }
  }
  if (role == null) {
    return AppRoutes.landing;
  }
  switch (role) {
    case UserRole.affectedUser:
      final id = prefs.getString(SessionKeys.graphUserId);
      if (id != null && id.isNotEmpty) {
        return AppRoutes.victimHome;
      }
      return AppRoutes.landing;
    case UserRole.volunteer:
      final id = prefs.getString(SessionKeys.graphVolunteerId);
      if (id != null && id.isNotEmpty) {
        return AppRoutes.volunteerHome;
      }
      return AppRoutes.landing;
    case UserRole.organization:
      final id = prefs.getString(SessionKeys.graphOrganizationId);
      if (id != null && id.isNotEmpty) {
        return AppRoutes.organizationDashboard;
      }
      return AppRoutes.landing;
  }
}

Future<void> _clearStaleAuth(SharedPreferences prefs) async {
  for (final k in [
    SessionKeys.authToken,
    SessionKeys.role,
    SessionKeys.graphUserId,
    SessionKeys.graphVolunteerId,
    SessionKeys.graphOrganizationId,
    SessionKeys.zoneId,
    SessionKeys.organizationType,
    SessionKeys.volunteerAvailability,
    SessionKeys.userHouseholdSize,
    SessionKeys.userElderlyCount,
    SessionKeys.userOxygenDependency,
    SessionKeys.userPreferredLanguage,
    SessionKeys.userMobilityConcern,
    SessionKeys.lastIncidentId,
  ]) {
    await prefs.remove(k);
  }
}

Future<void> _persistMe(SharedPreferences prefs, AuthMeDto me) async {
  switch (me.role) {
    case 'victim':
      await prefs.setString(SessionKeys.role, UserRole.affectedUser.name);
      await prefs.setString(SessionKeys.graphUserId, me.id);
      if (me.zoneId != null && me.zoneId!.isNotEmpty) {
        await prefs.setString(SessionKeys.zoneId, me.zoneId!);
      }
      if (me.householdSize != null) {
        await prefs.setString(SessionKeys.userHouseholdSize, '${me.householdSize}');
      }
      if (me.elderlyCount != null) {
        await prefs.setString(SessionKeys.userElderlyCount, '${me.elderlyCount}');
      }
      if (me.oxygenDependency != null) {
        await prefs.setString(SessionKeys.userOxygenDependency, me.oxygenDependency! ? '1' : '0');
      }
      if (me.preferredLanguage != null && me.preferredLanguage!.isNotEmpty) {
        await prefs.setString(SessionKeys.userPreferredLanguage, me.preferredLanguage!);
      }
      if (me.mobilityConcern != null) {
        await prefs.setString(SessionKeys.userMobilityConcern, me.mobilityConcern! ? '1' : '0');
      }
      await prefs.remove(SessionKeys.graphVolunteerId);
      await prefs.remove(SessionKeys.graphOrganizationId);
      break;
    case 'volunteer':
      await prefs.setString(SessionKeys.role, UserRole.volunteer.name);
      await prefs.setString(SessionKeys.graphVolunteerId, me.id);
      if (me.zoneId != null && me.zoneId!.isNotEmpty) {
        await prefs.setString(SessionKeys.zoneId, me.zoneId!);
      }
      if (me.availability != null && me.availability!.isNotEmpty) {
        await prefs.setString(SessionKeys.volunteerAvailability, me.availability!);
      }
      await prefs.remove(SessionKeys.graphUserId);
      await prefs.remove(SessionKeys.graphOrganizationId);
      break;
    case 'organization':
      await prefs.setString(SessionKeys.role, UserRole.organization.name);
      await prefs.setString(SessionKeys.graphOrganizationId, me.id);
      if (me.zoneId != null && me.zoneId!.isNotEmpty) {
        await prefs.setString(SessionKeys.zoneId, me.zoneId!);
      }
      if (me.orgType != null && me.orgType!.isNotEmpty) {
        await prefs.setString(SessionKeys.organizationType, me.orgType!);
      }
      await prefs.remove(SessionKeys.graphUserId);
      await prefs.remove(SessionKeys.graphVolunteerId);
      break;
    default:
      await _clearStaleAuth(prefs);
      break;
  }
}

String _homeForRole(String apiRole) {
  switch (apiRole) {
    case 'victim':
      return AppRoutes.victimHome;
    case 'volunteer':
      return AppRoutes.volunteerHome;
    case 'organization':
      return AppRoutes.organizationDashboard;
    default:
      return AppRoutes.landing;
  }
}

/// Validates stored JWT with `/auth/me` and syncs prefs; falls back to legacy session or landing.
Future<String> resolveAppEntryPoint(SharedPreferences prefs, Dio dio) async {
  try {
    await dio.get<Map<String, dynamic>>('/health');
  } catch (_) {
    // Offline or server down — still try legacy routing.
  }

  final token = prefs.getString(SessionKeys.authToken);
  if (token == null || token.isEmpty) {
    return resolveStartupLocation(prefs);
  }

  dio.options.headers['Authorization'] = 'Bearer $token';
  try {
    final r = await dio.get<Map<String, dynamic>>('/auth/me');
    final data = r.data;
    if (data == null) {
      await _clearStaleAuth(prefs);
      return AppRoutes.landing;
    }
    final me = AuthMeDto.fromJson(data);
    if (me.userRole == null) {
      await _clearStaleAuth(prefs);
      return AppRoutes.landing;
    }
    await _persistMe(prefs, me);
    return _homeForRole(me.role);
  } catch (_) {
    await _clearStaleAuth(prefs);
    return AppRoutes.landing;
  }
}
