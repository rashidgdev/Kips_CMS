# KIPS CMS — Mobile App

React Native (Expo) mobile client for the KIPS College Kasur Campus Management System. Consumes the
Django REST API in this repo's root (`/api/v1/...`) — the Django project is the single source of
truth for business logic; this app is a thin client with no duplicated rules.

Every role from the web app (Student, Teacher, HOD, Campus Coordinator, Accountant, College
Administrator) has the same capabilities here, adapted to mobile UX rather than a copy of the
desktop layout — see [Architecture](#architecture) below for specifics.

## Prerequisites

- Node.js 18+ and npm (already installed if you've been running the backend's tooling)
- The **Expo Go** app on your phone (Android: Play Store, iOS: App Store) — **update it to the
  latest version before connecting**. This project targets Expo **SDK 54**; if Expo Go reports a
  different supported SDK (Settings → App Info inside Expo Go), the project's `expo` version needs
  to match it (`npx expo install expo@<matching version>` then `npx expo install --fix`).
- The Django backend running and reachable from your phone (see below).

## Setup

```
cd mobile
npm install
cp .env.example .env
```

Edit `.env` and set `EXPO_PUBLIC_API_BASE_URL` to point at your Django server. Comments in
`.env.example` explain how to find your PC's LAN IP. Then start Django reachable on the network:

```
# from the repo root
python manage.py runserver 0.0.0.0:8000
```

...and add that IP to `DJANGO_ALLOWED_HOSTS` in the root `.env` (comma-separated).

## Running the app

```
npx expo start
```

Scan the printed QR code with Expo Go (Android: in-app scanner; iPhone: the regular Camera app).
Your phone and PC must be on the **same Wi-Fi network**.

### If Wi-Fi is slow or the app hangs on "downloading update"

Some networks (weak signal, router client isolation, or Hyper-V/WSL2's virtual network adapter
shows up as your "Wi-Fi" IP on some Windows setups) make the initial JS bundle transfer very slow
or unreliable over the LAN. The reliable fallback is **USB debugging**, which bypasses Wi-Fi
entirely:

1. On your phone: **Settings → About phone** → tap "Build number" 7 times to unlock Developer
   Options, then **Settings → Developer options** → enable **USB debugging**.
2. Plug the phone into your PC via USB and allow the debugging prompt that appears on the phone.
3. Install [platform-tools](https://developer.android.com/tools/releases/platform-tools) (`adb`)
   if you don't already have it, then:
   ```
   adb reverse tcp:8081 tcp:8081
   adb reverse tcp:8000 tcp:8000
   ```
4. Set `.env`'s `EXPO_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1` (via the USB tunnel,
   "localhost" on the phone now means "this PC").
5. `npx expo start --localhost`, then either scan the QR with Expo Go, or launch directly:
   ```
   adb shell am start -a android.intent.action.VIEW -d "exp://127.0.0.1:8081"
   ```

Switch back to the LAN instructions above any time by reverting `.env` and restarting without
`--localhost`.

## Architecture

```
src/
  app/                Expo Router screens (file-based routing)
    (auth)/            Login, forced change-password
    (app)/
      (tabs)/           Role-based bottom tab bar (see below)
      <module>/...      Pushed detail/create/edit screens per module
  features/            Domain logic: types + React Query hooks per module
    <module>/api.ts     Typed fetch hooks, one per API endpoint
    <module>/types.ts   TypeScript types mirroring the Django serializers exactly
  components/ui/       Reusable primitives (Button, Card, Input, ChipPicker, Badge, StatCard,
                        EmptyState, LoadingState, ErrorState) — every screen is built from these
  lib/
    api/client.ts       Typed fetch wrapper: attaches the JWT, retries once after a silent
                        token refresh on 401, throws a typed ApiError otherwise
    auth/               AuthContext (session state, SecureStore-backed token persistence)
    forms/              applyServerErrors() maps Django/DRF field errors onto react-hook-form
    pdf.ts              Authenticated PDF download + native share sheet
```

**Adding a new screen or role:** add a `features/<module>/{types,api}.ts` pair mirroring the
Django serializer fields exactly, then a route file under `app/(app)/` that composes the shared
`components/ui` primitives. To add a new role, extend `NAV_CONFIG` in
`src/constants/navConfig.ts` — everything else (route guards, tab visibility) reads from it.

**Role-based navigation:** `src/constants/navConfig.ts` mirrors the Django web app's own
`apps/common/context_processors.py::NAV_CONFIG` — same screens per role. It only controls what's
*shown*; every screen's actual data access is enforced server-side (a 403 is handled generically
by the API client), exactly like the web app. Busier roles get 4 primary tabs + a "More" tab
holding the rest, since a phone can't fit 6-8 top-level tabs the way a desktop sidebar can.

**Auth:** JWT access/refresh tokens in `expo-secure-store` (encrypted keychain/keystore). On a 401,
the API client attempts one silent refresh before forcing logout. `must_change_password` (set on
every admin-created account) routes to a forced change-password screen before anything else,
mirroring the web's `ForcePasswordChangeMiddleware`.

**Forms:** react-hook-form + zod for client-side validation (empty/malformed field checks only —
UX sugar, not business rules). The Django form/serializer on the server is always the real source
of truth; its error responses are mapped back onto the form via `applyServerErrors()` regardless
of what client-side validation allowed through.

## Known simplifications

- **Bulk Excel import** of students/teachers stays web-only (file-upload UX doesn't map cleanly to
  a first mobile pass).
- **Time slot generation** (the web's "split a day into N lectures with breaks" wizard) isn't
  built as a mobile screen yet — individual time slots can still be created/edited/deleted from
  Administration → Time Slots.
- **Push notifications** aren't implemented — the backend has no notification model or endpoint to
  poll (the web app only has one-shot session-flash messages, no API equivalent).
- **Offline support** means clear error states and retry, not working fully offline — there's no
  local database or background sync.

## Verification

Every module's API integration was verified against the live Django server (isolated throwaway
test data, real HTTP requests asserting exact response shapes match the TypeScript types) during
development — see the git history for the per-phase verification scripts. On the client side:
`npx tsc --noEmit` (type check), `npx eslint src` (lint), and `npx expo export` (confirms the
Metro bundler builds successfully) all pass clean. Visual/interaction testing happened on a
physical Android device via Expo Go throughout.

## Tech stack

Expo + Expo Router (TypeScript, SDK 54) · NativeWind (Tailwind for React Native) · TanStack Query
· react-hook-form + zod · expo-secure-store · expo-image-picker · expo-file-system + expo-sharing
