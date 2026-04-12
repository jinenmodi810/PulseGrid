class UpdateVolunteerCreditsUseCase {
  const UpdateVolunteerCreditsUseCase();

  // TODO(Phase1): persist credits via repository + storage events.
  int call({required int currentCredits, required int delta}) {
    final next = currentCredits + delta;
    return next < 0 ? 0 : next;
  }
}
