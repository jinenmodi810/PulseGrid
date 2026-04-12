import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/utils/result.dart';
import '../../../../core/widgets/app_button.dart';
import '../../domain/register_organization_payload.dart';
import '../../../organization/presentation/providers/organization_providers.dart';
import '../providers/auth_providers.dart';
import '../widgets/zone_chip_selector.dart';

class OrganizationRegistrationScreen extends ConsumerStatefulWidget {
  const OrganizationRegistrationScreen({super.key});

  @override
  ConsumerState<OrganizationRegistrationScreen> createState() => _OrganizationRegistrationScreenState();
}

class _OrganizationRegistrationScreenState extends ConsumerState<OrganizationRegistrationScreen> {
  final _orgName = TextEditingController();
  final _contactName = TextEditingController();
  final _contactPhone = TextEditingController();
  final _contactEmail = TextEditingController();
  final _password = TextEditingController();
  String _zoneId = '';
  String _orgType = 'ngo';
  bool _busy = false;

  static const _types = ['hospital', 'ngo', 'ambulance', 'rescue', 'shelter'];

  @override
  void dispose() {
    _orgName.dispose();
    _contactName.dispose();
    _contactPhone.dispose();
    _contactEmail.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_zoneId.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Choose a service zone.')));
      return;
    }
    setState(() => _busy = true);
    final uc = ref.read(registerOrganizationAccountUsecaseProvider);
    final r = await uc.call(
      RegisterOrganizationPayload(
        organizationName: _orgName.text.trim(),
        organizationType: _orgType,
        contactName: _contactName.text.trim(),
        contactPhone: _contactPhone.text.trim(),
        contactEmail: _contactEmail.text.trim(),
        password: _password.text,
        zoneId: _zoneId,
        coverageZoneIds: [_zoneId],
      ),
    );
    if (!mounted) {
      return;
    }
    setState(() => _busy = false);
    switch (r) {
      case Success():
        ref.invalidate(organizationOverviewProvider);
        ref.invalidate(organizationIncidentsProvider);
        context.go(AppRoutes.organizationDashboard);
      case Failure(:final error):
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final pad = MediaQuery.sizeOf(context).width >= 390 ? 22.0 : 18.0;
    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Organization access'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: ListView(
          padding: EdgeInsets.fromLTRB(pad, 12, pad, 28),
          children: [
            Text(
              'Register your organization to receive routed incidents and manage capacity.',
              style: AppTextStyles.heroSupporting(),
            ),
            const SizedBox(height: 20),
            Text('Organization', style: AppTextStyles.titleMedium().copyWith(fontSize: 15)),
            const SizedBox(height: 10),
            TextFormField(
              controller: _orgName,
              decoration: const InputDecoration(labelText: 'Organization name', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 14),
            DropdownButtonFormField<String>(
              value: _orgType,
              decoration: const InputDecoration(labelText: 'Organization type', border: OutlineInputBorder()),
              items: _types
                  .map((t) => DropdownMenuItem(value: t, child: Text(t[0].toUpperCase() + t.substring(1))))
                  .toList(),
              onChanged: (v) => setState(() => _orgType = v ?? 'ngo'),
            ),
            const SizedBox(height: 22),
            Text('Primary contact', style: AppTextStyles.titleMedium().copyWith(fontSize: 15)),
            const SizedBox(height: 10),
            TextFormField(
              controller: _contactName,
              textCapitalization: TextCapitalization.words,
              decoration: const InputDecoration(labelText: 'Contact name', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _contactPhone,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(labelText: 'Contact phone', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _contactEmail,
              keyboardType: TextInputType.emailAddress,
              autocorrect: false,
              decoration: const InputDecoration(
                labelText: 'Contact email (sign-in)',
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
            Text('Primary service zone', style: AppTextStyles.titleMedium().copyWith(fontSize: 15)),
            const SizedBox(height: 8),
            ZoneChipSelector(
              selectedZoneId: _zoneId,
              label: 'Service zone',
              onSelected: (id) => setState(() => _zoneId = id),
            ),
            const SizedBox(height: 28),
            AppButton(
              label: _busy ? 'Saving…' : 'Continue to operations',
              onPressed: _busy ? null : _submit,
              hero: true,
            ),
          ],
        ),
    );
  }
}
