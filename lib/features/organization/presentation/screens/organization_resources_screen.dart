import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/utils/result.dart';
import '../providers/organization_providers.dart';

class OrganizationResourcesScreen extends ConsumerStatefulWidget {
  const OrganizationResourcesScreen({super.key});

  @override
  ConsumerState<OrganizationResourcesScreen> createState() => _OrganizationResourcesScreenState();
}

class _OrganizationResourcesScreenState extends ConsumerState<OrganizationResourcesScreen> {
  int _beds = 0;
  int _oxygen = 0;
  int _amb = 0;
  int _shelter = 0;
  int _food = 0;
  int _rescue = 0;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(organizationOverviewProvider.future).then((o) {
        final c = o.capacity;
        setState(() {
          _beds = (c['beds_available'] as num?)?.toInt() ?? 0;
          _oxygen = (c['oxygen_units'] as num?)?.toInt() ?? 0;
          _amb = (c['ambulances_available'] as num?)?.toInt() ?? 0;
          _shelter = (c['shelter_units'] as num?)?.toInt() ?? 0;
          _food = (c['food_capacity_units'] as num?)?.toInt() ?? 0;
          _rescue = (c['rescue_units'] as num?)?.toInt() ?? 0;
        });
      });
    });
  }

  Future<void> _save() async {
    final oid = await ref.read(organizationSessionIdProvider.future);
    setState(() => _busy = true);
    final repo = ref.read(organizationRepositoryProvider);
    final r = await repo.updateCapacity(oid, {
      'beds_available': _beds,
      'oxygen_units': _oxygen,
      'ambulances_available': _amb,
      'shelter_units': _shelter,
      'food_capacity_units': _food,
      'rescue_units': _rescue,
    });
    if (!mounted) return;
    setState(() => _busy = false);
    switch (r) {
      case Success():
        ref.invalidate(organizationOverviewProvider);
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Capacity updated.')));
      case Failure(:final error):
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Resources & capacity'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text('Adjust what you can commit right now. PulseGrid uses this for routing context.', style: AppTextStyles.bodyMuted()),
          const SizedBox(height: 20),
          _Counter('Beds available', _beds, (v) => setState(() => _beds = v)),
          _Counter('Oxygen / respiratory units', _oxygen, (v) => setState(() => _oxygen = v)),
          _Counter('Ambulances available', _amb, (v) => setState(() => _amb = v)),
          _Counter('Shelter units', _shelter, (v) => setState(() => _shelter = v)),
          _Counter('Food capacity (meals/day est.)', _food, (v) => setState(() => _food = v)),
          _Counter('Rescue task units', _rescue, (v) => setState(() => _rescue = v)),
          const SizedBox(height: 24),
          FilledButton(onPressed: _busy ? null : _save, child: Text(_busy ? 'Saving…' : 'Save capacity')),
        ],
      ),
    );
  }
}

class _Counter extends StatelessWidget {
  const _Counter(this.label, this.value, this.onChanged);

  final String label;
  final int value;
  final void Function(int) onChanged;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Row(
        children: [
          Expanded(child: Text(label, style: AppTextStyles.body())),
          IconButton(onPressed: () => onChanged((value - 1).clamp(0, 99999)), icon: const Icon(Icons.remove_circle_outline)),
          Text('$value', style: AppTextStyles.titleMedium()),
          IconButton(onPressed: () => onChanged((value + 1).clamp(0, 99999)), icon: const Icon(Icons.add_circle_outline)),
        ],
      ),
    );
  }
}
