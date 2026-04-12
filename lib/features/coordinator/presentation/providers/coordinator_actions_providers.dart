import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../app/providers.dart';
import '../../data/coordinator_actions_repository.dart';

final coordinatorActionsRepositoryProvider = Provider<CoordinatorActionsRepository>((ref) {
  return CoordinatorActionsRepository(ref.watch(apiClientProvider));
});
