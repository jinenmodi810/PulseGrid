import '../../data/models/incident_model.dart';
import '../../core/utils/scoring_utils.dart';

class CalculatePriorityUseCase {
  const CalculatePriorityUseCase();

  // TODO(Phase1): replace placeholder with real scoring inputs.
  double call({required IncidentModel incident}) {
    return ScoringUtils.placeholderPriorityScore();
  }
}
