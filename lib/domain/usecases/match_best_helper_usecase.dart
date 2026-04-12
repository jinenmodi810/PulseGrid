import '../../data/models/incident_model.dart';
import '../../data/models/volunteer_model.dart';

class MatchBestHelperUseCase {
  const MatchBestHelperUseCase();

  // TODO(Phase1): implement skill and proximity aware matching.
  VolunteerModel? call({required IncidentModel incident, required List<VolunteerModel> volunteers}) {
    if (volunteers.isEmpty) {
      return null;
    }
    return volunteers.first;
  }
}
