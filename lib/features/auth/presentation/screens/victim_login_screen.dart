import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/utils/result.dart';
import '../providers/auth_providers.dart';

class VictimLoginScreen extends ConsumerStatefulWidget {
  const VictimLoginScreen({super.key});

  @override
  ConsumerState<VictimLoginScreen> createState() => _VictimLoginScreenState();
}

class _VictimLoginScreenState extends ConsumerState<VictimLoginScreen> {
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
    final uc = ref.read(loginVictimUsecaseProvider);
    final r = await uc.call(email: _email.text.trim(), password: _password.text);
    if (!mounted) {
      return;
    }
    setState(() => _busy = false);
    switch (r) {
      case Success():
        ref.invalidate(victimProfileBySessionProvider);
        context.go(AppRoutes.victimHome);
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
        title: const Text('Sign in'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: ListView(
          padding: EdgeInsets.fromLTRB(pad, 16, pad, 28),
          children: [
            Text('Welcome back', style: AppTextStyles.titleMedium().copyWith(fontSize: 22)),
            const SizedBox(height: 8),
            Text('Use the email and password you registered with.', style: AppTextStyles.heroSupporting()),
            const SizedBox(height: 24),
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
            const SizedBox(height: 28),
            FilledButton(
              onPressed: _busy ? null : _submit,
              child: _busy
                  ? const SizedBox(height: 22, width: 22, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('Continue'),
            ),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () => context.pushReplacement(AppRoutes.registerUser),
              child: const Text('Create an account'),
            ),
          ],
        ),
    );
  }
}
