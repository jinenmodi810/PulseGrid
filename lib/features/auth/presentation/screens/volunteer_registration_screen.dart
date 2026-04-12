import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/utils/result.dart';
import '../../domain/register_volunteer_payload.dart';
import '../constants/volunteer_capability_options.dart';
import '../constants/zone_options.dart';
import '../providers/auth_providers.dart';
import '../widgets/zone_chip_selector.dart';
import '../../../volunteer/presentation/providers/volunteer_task_providers.dart';

class VolunteerRegistrationScreen extends ConsumerStatefulWidget {
  const VolunteerRegistrationScreen({super.key});

  @override
  ConsumerState<VolunteerRegistrationScreen> createState() => _VolunteerRegistrationScreenState();
}

class _VolunteerRegistrationScreenState extends ConsumerState<VolunteerRegistrationScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _name = TextEditingController();
  final _phone = TextEditingController();
  final _availability = TextEditingController();
  String _transport = 'car';
  String _zone = kAuthZoneIds.first;
  bool _organizationVerified = false;
  bool _submitting = false;

  final Set<String> _languages = {'en'};
  final Set<String> _skills = {'general'};
  final Set<String> _supportTypes = {'general_support'};

  void _toggleLang(String id, bool selected) {
    setState(() {
      if (selected) {
        _languages.add(id);
      } else if (_languages.length > 1) {
        _languages.remove(id);
      }
    });
  }

  void _toggleSkill(String id, bool selected) {
    setState(() {
      if (selected) {
        _skills.add(id);
      } else if (_skills.length > 1) {
        _skills.remove(id);
      }
    });
  }

  void _toggleSupport(String id, bool selected) {
    setState(() {
      if (selected) {
        _supportTypes.add(id);
      } else if (_supportTypes.length > 1) {
        _supportTypes.remove(id);
      }
    });
  }

  Widget _filterChip({
    required String label,
    required bool selected,
    required ValueChanged<bool> onSelected,
  }) {
    return FilterChip(
      label: Text(label),
      selected: selected,
      onSelected: onSelected,
      showCheckmark: true,
      selectedColor: AppColors.iconSoftFill,
      checkmarkColor: AppColors.primary,
      side: BorderSide(color: selected ? AppColors.primary : AppColors.border),
      labelStyle: AppTextStyles.body().copyWith(
        color: selected ? AppColors.primary : AppColors.textPrimary,
        fontWeight: selected ? FontWeight.w600 : FontWeight.w500,
      ),
    );
  }

  Future<void> _submit() async {
    setState(() => _submitting = true);
    final langs = _languages.toList()..sort();
    final skills = _skills.toList()..sort();
    final supports = _supportTypes.toList()..sort();
    final payload = RegisterVolunteerPayload(
      email: _email.text.trim(),
      password: _password.text,
      fullName: _name.text.trim(),
      phone: _phone.text.trim(),
      languages: langs,
      zoneId: _zone,
      availability: _availability.text.trim(),
      transportAccess: _transport,
      skills: skills,
      supportTypes: supports,
      verified: _organizationVerified,
    );
    final usecase = ref.read(registerVolunteerAccountUsecaseProvider);
    final result = await usecase.call(payload);
    if (!mounted) {
      return;
    }
    setState(() => _submitting = false);
    switch (result) {
      case Success():
        ref.invalidate(volunteerProfileBySessionProvider);
        context.go(AppRoutes.volunteerHome);
      case Failure(:final error):
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error), behavior: SnackBarBehavior.floating),
        );
    }
  }

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    _name.dispose();
    _phone.dispose();
    _availability.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final pad = MediaQuery.sizeOf(context).width >= 390 ? 22.0 : 18.0;

    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Volunteer registration'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go(AppRoutes.roleSelect),
        ),
      ),
      body: ListView(
          padding: EdgeInsets.fromLTRB(pad, 8, pad, 28),
          children: [
            Text(
              'Capability profile is used for intelligent matching. '
              'Pick everything that applies.',
              style: AppTextStyles.heroSupporting(),
            ),
            const SizedBox(height: 20),
            Text('Account', style: AppTextStyles.titleMedium().copyWith(fontSize: 15)),
            const SizedBox(height: 10),
            TextFormField(
              controller: _email,
              keyboardType: TextInputType.emailAddress,
              autocorrect: false,
              decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _password,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Password',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),
            Text('Identity', style: AppTextStyles.titleMedium().copyWith(fontSize: 15)),
            const SizedBox(height: 10),
            TextFormField(
              controller: _name,
              textCapitalization: TextCapitalization.words,
              decoration: const InputDecoration(
                labelText: 'Full name',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _phone,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(
                labelText: 'Phone',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            Text('Languages you speak', style: AppTextStyles.titleMedium().copyWith(fontSize: 14)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _filterChip(
                  label: 'English',
                  selected: _languages.contains('en'),
                  onSelected: (s) => _toggleLang('en', s),
                ),
                _filterChip(
                  label: 'Spanish',
                  selected: _languages.contains('es'),
                  onSelected: (s) => _toggleLang('es', s),
                ),
                _filterChip(
                  label: 'Other',
                  selected: _languages.contains('other'),
                  onSelected: (s) => _toggleLang('other', s),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ZoneChipSelector(
              selectedZoneId: _zone,
              onSelected: (z) => setState(() => _zone = z),
              label: 'Primary response zone',
            ),
            const SizedBox(height: 20),
            Text('Skills', style: AppTextStyles.titleMedium().copyWith(fontSize: 14)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final id in kVolunteerSkillChipIds)
                  _filterChip(
                    label: skillChipLabel(id),
                    selected: _skills.contains(id),
                    onSelected: (s) => _toggleSkill(id, s),
                  ),
              ],
            ),
            const SizedBox(height: 20),
            Text('Support types', style: AppTextStyles.titleMedium().copyWith(fontSize: 14)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final id in kVolunteerSupportTypeIds)
                  _filterChip(
                    label: supportTypeLabel(id),
                    selected: _supportTypes.contains(id),
                    onSelected: (s) => _toggleSupport(id, s),
                  ),
              ],
            ),
            const SizedBox(height: 20),
            Text('Logistics', style: AppTextStyles.titleMedium().copyWith(fontSize: 15)),
            const SizedBox(height: 10),
            DropdownButtonFormField<String>(
              value: _transport,
              decoration: const InputDecoration(
                labelText: 'Transport access',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 'car', child: Text('Private vehicle')),
                DropdownMenuItem(value: 'public_transit', child: Text('Public transit')),
                DropdownMenuItem(value: 'bicycle', child: Text('Bicycle')),
                DropdownMenuItem(value: 'none', child: Text('None / local only')),
              ],
              onChanged: (v) => setState(() => _transport = v ?? 'car'),
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _availability,
              decoration: const InputDecoration(
                labelText: 'Availability',
                border: OutlineInputBorder(),
                hintText: 'e.g. Weekends, evenings',
                helperText: 'Avoid marking “unavailable” unless you truly cannot respond.',
              ),
            ),
            const SizedBox(height: 8),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: Text('Verified responder', style: AppTextStyles.body()),
              subtitle: Text(
                'Enable if an organization has already verified your identity.',
                style: AppTextStyles.microcopy(),
              ),
              value: _organizationVerified,
              onChanged: (v) => setState(() => _organizationVerified = v),
            ),
            const SizedBox(height: 20),
            FilledButton(
              onPressed: _submitting ? null : _submit,
              child: _submitting
                  ? const SizedBox(
                      height: 22,
                      width: 22,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Continue'),
            ),
          ],
        ),
    );
  }
}
