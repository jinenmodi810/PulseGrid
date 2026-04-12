import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/layout/screen_insets.dart';
import '../../../../app/providers.dart';
import '../../../../core/enums/user_role.dart';
import '../../../../core/utils/result.dart';
import '../../../../core/widgets/app_button.dart';
import '../../../auth/presentation/constants/zone_options.dart';
import '../../domain/help_request_submit_payload.dart';
import '../../domain/local_priority_preview.dart';
import '../providers/help_request_providers.dart';
import '../widgets/priority_preview_card.dart';
import '../widgets/request_form.dart';

class RequestHelpScreen extends ConsumerStatefulWidget {
  const RequestHelpScreen({super.key});

  @override
  ConsumerState<RequestHelpScreen> createState() => _RequestHelpScreenState();
}

class _RequestHelpScreenState extends ConsumerState<RequestHelpScreen> {
  final _peopleController = TextEditingController(text: '1');
  final _noteController = TextEditingController();

  String _incidentType = kIncidentTypes.first;
  String _severity = 'medium';
  String _zoneId = kAuthZoneIds.first;
  bool _elderly = false;
  bool _childPresent = false;
  bool _injury = false;
  bool _oxygenRequired = false;
  bool _shelterNeeded = false;
  bool _foodNeeded = false;
  bool _transportNeeded = false;
  bool _submitting = false;

  bool _peopleTouched = false;
  bool _elderlyTouched = false;
  bool _oxygenTouched = false;
  bool _suppressPeopleListener = false;
  bool _showProfileHint = false;

  void _onPeopleEdited() {
    if (_suppressPeopleListener) {
      return;
    }
    if (!_peopleTouched) {
      _peopleTouched = true;
    }
    setState(() {});
  }

  @override
  void initState() {
    super.initState();
    _peopleController.addListener(_onPeopleEdited);
    Future<void>(() async {
      final storage = ref.read(storageServiceProvider);
      final zone = await storage.getString(SessionKeys.zoneId);
      final hh = await storage.getString(SessionKeys.userHouseholdSize);
      final ec = await storage.getString(SessionKeys.userElderlyCount);
      final ox = await storage.getString(SessionKeys.userOxygenDependency);
      if (!mounted) {
        return;
      }
      var hint = false;
      if (zone != null && zone.isNotEmpty) {
        setState(() => _zoneId = zone);
        hint = true;
      }
      final hInt = int.tryParse(hh ?? '');
      if (hInt != null && hInt > 0) {
        _suppressPeopleListener = true;
        _peopleController.text = '$hInt';
        _suppressPeopleListener = false;
        hint = true;
      }
      final elderlyN = int.tryParse(ec ?? '0') ?? 0;
      if (elderlyN > 0) {
        setState(() => _elderly = true);
        hint = true;
      }
      if (ox == '1') {
        setState(() => _oxygenRequired = true);
        hint = true;
      }
      if (hint) {
        setState(() => _showProfileHint = true);
      }
    });
  }

  @override
  void dispose() {
    _peopleController.removeListener(_onPeopleEdited);
    _peopleController.dispose();
    _noteController.dispose();
    super.dispose();
  }

  int _parsePeopleCount() {
    final raw = int.tryParse(_peopleController.text.trim());
    if (raw == null || raw < 1) return 1;
    return raw > 500 ? 500 : raw;
  }

  LocalPriorityPreview _preview() {
    return LocalPriorityPreview.fromDraft(
      severity: _severity,
      peopleCount: _parsePeopleCount(),
      elderly: _elderly,
      childPresent: _childPresent,
      injury: _injury,
      oxygenRequired: _oxygenRequired,
      shelterNeeded: _shelterNeeded,
      foodNeeded: _foodNeeded,
      transportNeeded: _transportNeeded,
    );
  }

  Future<void> _submit() async {
    if (_zoneId.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select your current zone.')),
      );
      return;
    }
    setState(() => _submitting = true);
    final usecase = ref.read(submitHelpRequestUsecaseProvider);
    final payload = HelpRequestSubmitPayload(
      userId: '',
      incidentType: _incidentType,
      severity: _severity,
      peopleCount: _parsePeopleCount(),
      zoneId: _zoneId,
      elderly: _elderly,
      childPresent: _childPresent,
      injury: _injury,
      oxygenRequired: _oxygenRequired,
      shelterNeeded: _shelterNeeded,
      foodNeeded: _foodNeeded,
      transportNeeded: _transportNeeded,
      note: _noteController.text.trim(),
      useProfileForPeopleCount: !_peopleTouched,
      useProfileForElderly: !_elderlyTouched,
      useProfileForOxygenRequired: !_oxygenTouched,
    );
    final result = await usecase.call(payload);
    if (!mounted) return;
    setState(() => _submitting = false);
    switch (result) {
      case Success(:final data):
        if (data.profileDefaultsUsed.isNotEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Synced from your profile: ${data.profileDefaultsUsed.join(', ')}. '
                'You can still adjust on future requests.',
              ),
              behavior: SnackBarBehavior.floating,
            ),
          );
        }
        context.go(AppRoutes.incidentDetail(data.incidentId));
      case Failure(:final error):
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error)),
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    final preview = _preview();
    final profileHint = _showProfileHint
        ? 'Some details were filled from your profile to save time. '
            'Change a field to send your override instead of the saved default for that item.'
        : null;
    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        title: const Text('Request support'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () async {
            if (context.canPop()) {
              context.pop();
              return;
            }
            final role = await ref.read(sessionStoreProvider).readRole();
            if (!context.mounted) {
              return;
            }
            if (role == UserRole.affectedUser) {
              context.go(AppRoutes.victimHome);
            } else {
              context.go(AppRoutes.landing);
            }
          },
        ),
        actions: [
          IconButton(
            tooltip: 'Support directory',
            icon: const Icon(Icons.list_alt_outlined),
            onPressed: () => context.push(AppRoutes.supportDirectory),
          ),
          IconButton(
            tooltip: 'Profile',
            icon: const Icon(Icons.person_outline),
            onPressed: () => context.push(AppRoutes.profile),
          ),
        ],
      ),
      body: SafeArea(
        top: false,
        child: ListView(
          keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
          padding: ScreenInsets.compactHorizontal(context, horizontal: 16, top: 8, bottomExtra: 28),
          children: [
          PriorityPreviewCard(preview: preview),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(
                    'Voice SOS is not active yet. This button reserves the entry point; '
                    'ElevenLabs or cloud STT will populate structured fields, then POST /incidents with intake_source. '
                    'Backend stub: POST /incidents/voice-intake/preview.',
                    maxLines: 6,
                    overflow: TextOverflow.fade,
                  ),
                  behavior: SnackBarBehavior.floating,
                ),
              );
            },
            icon: const Icon(Icons.mic_none_outlined),
            label: Text(
              'Voice SOS (placeholder)',
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: Theme.of(context).textTheme.labelLarge,
            ),
          ),
          const SizedBox(height: 16),
          RequestForm(
            incidentType: _incidentType,
            onIncidentType: (v) => setState(() => _incidentType = v),
            severity: _severity,
            onSeverity: (v) => setState(() => _severity = v),
            peopleController: _peopleController,
            zoneId: _zoneId,
            onZoneId: (z) => setState(() => _zoneId = z),
            noteController: _noteController,
            elderly: _elderly,
            onElderly: (v) => setState(() {
              _elderly = v;
              _elderlyTouched = true;
            }),
            childPresent: _childPresent,
            onChildPresent: (v) => setState(() => _childPresent = v),
            injury: _injury,
            onInjury: (v) => setState(() => _injury = v),
            oxygenRequired: _oxygenRequired,
            onOxygenRequired: (v) => setState(() {
              _oxygenRequired = v;
              _oxygenTouched = true;
            }),
            shelterNeeded: _shelterNeeded,
            onShelterNeeded: (v) => setState(() => _shelterNeeded = v),
            foodNeeded: _foodNeeded,
            onFoodNeeded: (v) => setState(() => _foodNeeded = v),
            transportNeeded: _transportNeeded,
            onTransportNeeded: (v) => setState(() => _transportNeeded = v),
            profileSyncHint: profileHint,
          ),
          const SizedBox(height: 20),
          AppButton(
            label: _submitting ? 'Submitting…' : 'Submit help request',
            onPressed: _submitting ? null : _submit,
            hero: true,
          ),
        ],
        ),
      ),
    );
  }
}
