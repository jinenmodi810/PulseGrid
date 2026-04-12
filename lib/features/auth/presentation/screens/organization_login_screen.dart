import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/utils/result.dart';
import '../../../organization/presentation/providers/organization_providers.dart';
import '../providers/auth_providers.dart';

class OrganizationLoginScreen extends ConsumerStatefulWidget {
  const OrganizationLoginScreen({super.key});

  @override
  ConsumerState<OrganizationLoginScreen> createState() => _OrganizationLoginScreenState();
}

class _OrganizationLoginScreenState extends ConsumerState<OrganizationLoginScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _busy = false;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() => _busy = true);
    final r = await ref.read(loginOrganizationUsecaseProvider).call(
          email: _email.text.trim(),
          password: _password.text,
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
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error), behavior: SnackBarBehavior.floating),
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    final pad = MediaQuery.sizeOf(context).width >= 390 ? 22.0 : 18.0;
    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Organization sign in'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: ListView(
          padding: EdgeInsets.fromLTRB(pad, 16, pad, 28),
          children: [
            Text('Partner access', style: AppTextStyles.titleMedium().copyWith(fontSize: 22)),
            const SizedBox(height: 8),
            Text('Sign in with the contact email used for your organization.', style: AppTextStyles.heroSupporting()),
            const SizedBox(height: 24),
            TextFormField(
              controller: _email,
              keyboardType: TextInputType.emailAddress,
              autocorrect: false,
              decoration: const InputDecoration(labelText: 'Contact email', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _password,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 28),
            FilledButton(
              onPressed: _busy ? null : _submit,
              child: _busy
                  ? const SizedBox(height: 22, width: 22, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('Continue'),
            ),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () => context.pushReplacement(AppRoutes.registerOrganization),
              child: const Text('Register organization'),
            ),
          ],
        ),
    );
  }
}
