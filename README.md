# PulseGrid

PulseGrid is a **mobile-first** Flutter scaffold for a community crisis coordination and recovery product. Phase 0 focuses on a clean backbone: navigation, theming, mock-backed repositories, shared widgets, and placeholder feature surfaces—**not** production crisis logic.

## Prerequisites

- Flutter SDK (see `environment` in `pubspec.yaml` for the supported Dart SDK).
- Xcode / Android toolchain when targeting simulators or devices.

## Setup

1. Clone the repository and enter the project root.
2. Install dependencies:

   ```bash
   flutter pub get
   ```

3. Environment variables live in `.env` at the repo root (also listed under `flutter/assets` in `pubspec.yaml` so mobile builds can bundle it). Update:

   - `API_BASE_URL` — REST base URL for future `ApiClient` usage.
   - `GEMINI_API_KEY` — optional; **prefer a backend proxy** before shipping anything real.

4. Run the app:

   ```bash
   flutter run
   ```

   Chrome is fine for hackathon demos, but layouts are intended for phone-sized viewports first.

## Architecture (practical clean + feature-first)

- **`lib/app/`** — App shell: `PulseGridApp`, `GoRouter` configuration, theme tokens, global constants, Riverpod providers for cross-cutting services and repositories.
- **`lib/core/`** — Shared enums, utilities (`Result`, validators, dates, scoring placeholders), design-system widgets, and service facades (`StorageService`, `MockDataService`, `GeminiService`, `NotificationService`).
- **`lib/data/`** — Plain Dart models, asset-backed repositories, `JsonLoader`, and `ApiClient` (Dio) scaffolding.
- **`lib/domain/`** — Use cases and a thin `IncidentEntity` example showing where domain mapping will grow in Phase 1+.
- **`lib/features/*/`** — Feature modules with `presentation/` screens and widgets only; business rules stay in domain use cases or services.

### Mock-first data

All repositories read from `assets/json/mock_*.json`. Screens such as **Home** and **Support directory** demonstrate Riverpod `FutureProvider`s wired through repositories—swap implementations later without rewriting UI.

### Navigation

`GoRouter` paths are centralized in `AppRoutes` (`lib/app/constants/app_constants.dart`). Splash → Welcome → Role select → Home is the happy path; Home’s grid uses `context.push` so you can open every placeholder screen during QA.

## Tests

```bash
flutter test
```

## Phase checklist

- App boots without red screens.
- All routes reachable from Home or onboarding.
- Theme uses shared colors/typography (`GoogleFonts.inter`).
- Mock JSON is registered in `pubspec.yaml` and parsed safely.
- Widgets remain thin; TODOs mark upcoming business rules.
