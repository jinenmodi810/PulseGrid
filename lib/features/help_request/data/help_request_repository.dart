import 'package:dio/dio.dart';

import '../../../core/utils/result.dart';
import '../../../data/sources/remote/api_client.dart';
import '../domain/help_request_submit_payload.dart';
import '../domain/priority_preview_payload.dart';
import '../../incident_tracking/data/incident_detail_dto.dart';

class PriorityPreviewResult {
  const PriorityPreviewResult({required this.score, required this.label});

  final double score;
  final String label;

  factory PriorityPreviewResult.fromJson(Map<String, dynamic> json) {
    return PriorityPreviewResult(
      score: (json['priority_score'] as num?)?.toDouble() ?? 0,
      label: json['priority_label'] as String? ?? 'MEDIUM',
    );
  }
}

class CreateIncidentResult {
  const CreateIncidentResult({
    required this.incidentId,
    required this.status,
    required this.priorityScore,
    required this.priorityLabel,
    this.assignedHelperId,
    this.assignedHelperName,
    this.etaMinutes,
    required this.aiGuidance,
    this.preferredLanguage = '',
    this.profileDefaultsUsed = const [],
    this.emergencyContact,
    this.responseTier = '',
    this.escalationRequired = false,
    this.decisionSummary = '',
  });

  final String incidentId;
  final String status;
  final double priorityScore;
  final String priorityLabel;
  final String? assignedHelperId;
  final String? assignedHelperName;
  final int? etaMinutes;
  final String aiGuidance;
  final String preferredLanguage;
  final List<String> profileDefaultsUsed;
  final Map<String, dynamic>? emergencyContact;
  final String responseTier;
  final bool escalationRequired;
  final String decisionSummary;

  factory CreateIncidentResult.fromJson(Map<String, dynamic> json) {
    final helper = json['assigned_helper'];
    String? hid;
    String? hname;
    if (helper is Map<String, dynamic>) {
      hid = helper['id'] as String?;
      hname = helper['name'] as String?;
    }
    final rawEc = json['emergency_contact'];
    Map<String, dynamic>? ec;
    if (rawEc is Map<String, dynamic>) {
      ec = rawEc;
    }
    final pdu = json['profile_defaults_used'];
    final used = pdu is List ? pdu.map((e) => e.toString()).toList() : const <String>[];
    return CreateIncidentResult(
      incidentId: json['incident_id'] as String? ?? '',
      status: json['status'] as String? ?? 'open',
      priorityScore: (json['priority_score'] as num?)?.toDouble() ?? 0,
      priorityLabel: json['priority_label'] as String? ?? 'MEDIUM',
      assignedHelperId: hid,
      assignedHelperName: hname,
      etaMinutes: (json['eta_minutes'] as num?)?.toInt(),
      aiGuidance: json['ai_guidance'] as String? ?? '',
      preferredLanguage: json['preferred_language'] as String? ?? '',
      profileDefaultsUsed: used,
      emergencyContact: ec,
      responseTier: json['response_tier'] as String? ?? '',
      escalationRequired: json['escalation_required'] as bool? ?? false,
      decisionSummary: json['decision_summary'] as String? ?? '',
    );
  }
}

class HelpRequestRepository {
  HelpRequestRepository(this._api);

  final ApiClient _api;

  String _dioMessage(DioException e) {
    if (e.type == DioExceptionType.connectionError) {
      return "We can't reach PulseGrid right now. Check that the API is running.";
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

  Future<Result<PriorityPreviewResult, String>> previewPriority(PriorityPreviewPayload payload) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/incidents/preview-priority',
        data: payload.toJson(),
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(PriorityPreviewResult.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<CreateIncidentResult, String>> createIncident(HelpRequestSubmitPayload payload) async {
    try {
      final res = await _api.client.post<Map<String, dynamic>>(
        '/incidents/',
        data: payload.toJson(),
      );
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(CreateIncidentResult.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }

  Future<Result<IncidentDetailDto, String>> getIncident(String incidentId) async {
    try {
      final res = await _api.client.get<Map<String, dynamic>>('/incidents/$incidentId');
      final data = res.data;
      if (data == null) {
        return const Failure('Empty response');
      }
      return Success(IncidentDetailDto.fromJson(data));
    } on DioException catch (e) {
      return Failure(_dioMessage(e));
    } catch (e) {
      return Failure(e.toString());
    }
  }
}
