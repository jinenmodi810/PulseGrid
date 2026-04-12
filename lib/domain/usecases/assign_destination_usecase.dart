import '../../data/models/assignment_result_model.dart';
import '../../data/models/incident_model.dart';

class AssignDestinationUseCase {
  const AssignDestinationUseCase();

  // TODO(Phase1): integrate hospital/shelter capacity rules.
  AssignmentResultModel call({
    required IncidentModel incident,
    required String destinationId,
  }) {
    return AssignmentResultModel(
      incidentId: incident.id,
      assignedResourceId: destinationId,
      accepted: true,
    );
  }
}
