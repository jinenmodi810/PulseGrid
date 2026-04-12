import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/utils/result.dart';
import '../../domain/register_user_payload.dart';
import '../constants/zone_options.dart';
import '../providers/auth_providers.dart';
import '../widgets/zone_chip_selector.dart';

class UserRegistrationScreen extends ConsumerStatefulWidget {
  const UserRegistrationScreen({super.key});

  @override
  ConsumerState<UserRegistrationScreen> createState() => _UserRegistrationScreenState();
}

class _UserRegistrationScreenState extends ConsumerState<UserRegistrationScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _name = TextEditingController();
  final _phone = TextEditingController();
  final _household = TextEditingController();
  final _elderlyCount = TextEditingController(text: '0');
  final _ecName = TextEditingController();
  final _ecPhone = TextEditingController();
  final _ecRel = TextEditingController();
  String _language = 'en';
  String _zone = kAuthZoneIds.first;
  bool _mobilityConcern = false;
  bool _oxygenDependency = false;
  bool _submitting = false;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    _name.dispose();
    _phone.dispose();
    _household.dispose();
    _elderlyCount.dispose();
    _ecName.dispose();
    _ecPhone.dispose();
    _ecRel.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() => _submitting = true);
    final householdRaw = _household.text.trim();
    final household = householdRaw.isEmpty ? null : int.tryParse(householdRaw);
    final ec = int.tryParse(_elderlyCount.text.trim()) ?? 0;
    final payload = RegisterUserPayload(
      email: _email.text.trim(),
      password: _password.text,
      fullName: _name.text.trim(),
      phone: _phone.text.trim(),
      preferredLanguage: _language,
      homeZoneId: _zone,
      householdSize: household,
      elderlyCount: ec < 0 ? 0 : ec,
      mobilityConcern: _mobilityConcern,
      oxygenDependency: _oxygenDependency,
      emergencyContactName: _ecName.text.trim(),
      emergencyContactPhone: _ecPhone.text.trim(),
      emergencyContactRelationship: _ecRel.text.trim(),
    );
    final usecase = ref.read(registerAffectedUserUsecaseProvider);
    final result = await usecase.call(payload);
    if (!mounted) {
      return;
    }
    setState(() => _submitting = false);
    switch (result) {
      case Success():
        ref.invalidate(victimProfileBySessionProvider);
        context.go(AppRoutes.victimHome);
      case Failure(:final error):
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error), behavior: SnackBarBehavior.floating),
        );
    }
  }

  Widget _sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(top: 8, bottom: 8),
      child: Text(title, style: AppTextStyles.titleMedium().copyWith(fontSize: 15)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final pad = MediaQuery.sizeOf(context).width >= 390 ? 22.0 : 18.0;

    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Create your profile'),
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
              'We only ask for what helps responders reach you quickly. '
              'This profile also speeds up help requests later.',
              style: AppTextStyles.heroSupporting(),
            ),
            _sectionTitle('Account'),
            TextFormField(
              controller: _email,
              keyboardType: TextInputType.emailAddress,
              autocorrect: false,
              decoration: const InputDecoration(
                labelText: 'Email',
                border: OutlineInputBorder(),
              ),
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
            _sectionTitle('Identity'),
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
            const SizedBox(height: 14),
            DropdownButtonFormField<String>(
              value: _language,
              decoration: const InputDecoration(
                labelText: 'Preferred language',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 'en', child: Text('English')),
                DropdownMenuItem(value: 'es', child: Text('Spanish')),
                DropdownMenuItem(value: 'other', child: Text('Other')),
              ],
              onChanged: (v) => setState(() => _language = v ?? 'en'),
            ),
            const SizedBox(height: 16),
            ZoneChipSelector(
              selectedZoneId: _zone,
              onSelected: (z) => setState(() => _zone = z),
              label: 'Home zone',
            ),
            _sectionTitle('Household'),
            TextFormField(
              controller: _household,
              keyboardType: TextInputType.number,
              inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              decoration: const InputDecoration(
                labelText: 'Household size',
                border: OutlineInputBorder(),
                helperText: 'People you are responsible for in this emergency (optional)',
              ),
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _elderlyCount,
              keyboardType: TextInputType.number,
              inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              decoration: const InputDecoration(
                labelText: 'Elderly count in household',
                border: OutlineInputBorder(),
                helperText: 'Used to pre-flag elderly needs on help requests',
              ),
            ),
            _sectionTitle('Medical support'),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: Text('Mobility concern', style: AppTextStyles.body()),
              subtitle: Text(
                'Anyone in the home has difficulty moving quickly or needs mobility help.',
                style: AppTextStyles.microcopy(),
              ),
              value: _mobilityConcern,
              onChanged: (v) => setState(() => _mobilityConcern = v),
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: Text('Oxygen dependency', style: AppTextStyles.body()),
              subtitle: Text(
                'Someone relies on supplemental oxygen — we will pre-flag oxygen logistics on requests.',
                style: AppTextStyles.microcopy(),
              ),
              value: _oxygenDependency,
              onChanged: (v) => setState(() => _oxygenDependency = v),
            ),
            _sectionTitle('Emergency contact'),
            TextFormField(
              controller: _ecName,
              textCapitalization: TextCapitalization.words,
              decoration: const InputDecoration(
                labelText: 'Contact name',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _ecPhone,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(
                labelText: 'Contact phone',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _ecRel,
              textCapitalization: TextCapitalization.sentences,
              decoration: const InputDecoration(
                labelText: 'Relationship (optional)',
                border: OutlineInputBorder(),
                hintText: 'e.g. partner, neighbor',
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'TODO: SMS notifications to this contact will be added in a later phase.',
              style: AppTextStyles.microcopy().copyWith(color: AppColors.textTertiary),
            ),
            const SizedBox(height: 28),
            FilledButton(
              onPressed: _submitting ? null : _submit,
              child: _submitting
                  ? const SizedBox(
                      height: 22,
                      width: 22,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Continue to request help'),
            ),
          ],
        ),
    );
  }
}
