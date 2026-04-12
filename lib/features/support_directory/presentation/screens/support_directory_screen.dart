import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/providers.dart';
import '../../../../core/widgets/empty_state.dart';
import '../../../../core/widgets/loading_view.dart';
import '../widgets/support_contact_card.dart';

class SupportDirectoryScreen extends ConsumerWidget {
  const SupportDirectoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final contacts = ref.watch(supportContactsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Support directory'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: contacts.when(
        data: (items) {
          if (items.isEmpty) {
            return const EmptyState(
              title: 'No contacts yet',
              message:
                  'None returned from the API. After seeding Neo4j SupportContact nodes, GET /support/contacts will list them here.',
            );
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            separatorBuilder: (context, _) => const SizedBox(height: 10),
            itemBuilder: (context, index) {
              return SupportContactCard(contact: items[index]);
            },
          );
        },
        loading: () => const LoadingView(message: 'Loading contacts…'),
        error: (error, _) => EmptyState(
          title: 'Could not load contacts',
          message: error.toString(),
          actionLabel: 'Retry',
          onAction: () => ref.invalidate(supportContactsProvider),
        ),
      ),
    );
  }
}
