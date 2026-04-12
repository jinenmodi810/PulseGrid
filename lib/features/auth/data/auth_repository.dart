import 'package:dio/dio.dart';

import '../../../core/utils/result.dart';
import '../../../data/sources/remote/api_client.dart';
import '../domain/auth_me_dto.dart';
import '../domain/auth_sign_in_result.dart';
import '../domain/register_organization_payload.dart';
import '../domain/register_user_payload.dart';
import '../domain/register_volunteer_payload.dart';
import 'victim_user_profile_dto.dart';

class AdminLoginResult {
  const AdminLoginResult({required this.ok, this.detail, this.sessionMarker});

  final bool ok;
  final String? detail;
  final String? sessionMarker;

  factory AdminLoginResult.fromJson(Map<String, dynamic> json) {
    return AdminLoginResult(
      ok: json['ok'] as bool? ?? false,
      detail: json['detail'] as String?,
      sessionMarker: json['session_marker'] as String?,
    );
  }
}

class DashboardSummary {
  const DashboardSummary({
    required this.activeIncidents,
    required this.availableVolunteers,
    required this.hospitalsAvailable,
    required this.sheltersAvailable,
    required this.pendingRequests,
    required this.resolvedRequests,
  });

  final int activeIncidents;
  final int availableVolunteers;
  final int hospitalsAvailable;
  final int sheltersAvailable;
  final int pendingRequests;
  final int resolvedRequests;

  factory DashboardSummary.fromJson(Map<String, dynamic> json) {
    int n(String k) => (json[k] as num?)?.toInt() ?? 0;
    return DashboardSummary(
      activeIncidents: n('active_incidents'),
      availableVolunteers: n('available_volunteers'),
      hospitalsAvailable: n('hospitals_available'),
      sheltersAvailable: n('shelters_available'),
      pendingRequests: n('pending_requests'),
      resolvedRequests: n('resolved_requests'),
    );
  }
}

class AuthRepository {
  AuthRepository(this._api);

  final ApiClient _api;

  String _dioMessage(DioException e) {
    if (e.type == DioExceptionType.connectionError) {
      return "We can't reach PulseGrid right now. Check your connection and that the service is running.";
    }
    if (e.type == DioExceptionType.connectionTimeout || e.type == DioExceptionType.receiveTimeout) {
      return 'The server took too long to respond. Try again.';
    }
    final data = e.response?.data;
    if (data is Map && data['detail'] != null) {
      return data['detail'].toString();
    }
    return e.message ?? 'Something went wrong.';
  }

  Future<Result<AuthSignInResult, String>> registerVictim(RegisterUserPayload payload) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/auth/register-victim',
        data: payload.toJson(),
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(AuthSignInResult.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<AuthSignInResult, String>> loginVictim({required String email, required String password}) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/auth/login-victim',
        data: {'email': email, 'password': password},
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(AuthSignInResult.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<AuthSignInResult, String>> registerVolunteer(RegisterVolunteerPayload payload) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/auth/register-volunteer',
        data: payload.toJson(),
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(AuthSignInResult.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<AuthSignInResult, String>> loginVolunteer({required String email, required String password}) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/auth/login-volunteer',
        data: {'email': email, 'password': password},
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(AuthSignInResult.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<AuthSignInResult, String>> registerOrganization(RegisterOrganizationPayload payload) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/auth/register-organization',
        data: payload.toJson(),
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(AuthSignInResult.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<AuthSignInResult, String>> loginOrganization({required String email, required String password}) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/auth/login-organization',
        data: {'email': email, 'password': password},
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(AuthSignInResult.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<AuthMeDto, String>> authMe() async {
    try {
      final res = await _api.client.get<Map<String, dynamic>>('/auth/me');
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(AuthMeDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<AdminLoginResult, String>> adminLogin({required String email, required String password}) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/auth/admin-login',
        data: {'email': email, 'password': password},
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(AdminLoginResult.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<VictimUserProfileDto, String>> getUserProfile(String userId) async {
    try {
      final res = await _api.client.get<Map<String, dynamic>>('/users/$userId');
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(VictimUserProfileDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<DashboardSummary, String>> dashboardSummary() async {
    try {
      final res = await _api.client.get<Map<String, dynamic>>('/dashboard/summary');
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(DashboardSummary.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }
}
