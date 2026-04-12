import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/providers.dart';

Future<void> signOutAndGoLanding(WidgetRef ref, BuildContext context) async {
  await ref.read(sessionStoreProvider).clearSession();
  if (context.mounted) {
    context.go(AppRoutes.landing);
  }
}
