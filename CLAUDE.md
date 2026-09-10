# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Symphony BDK for Python — a bot development kit on top of the Symphony REST APIs (FINOS project). Package name on disk is `symphony`, import root `symphony.bdk`. Python >=3.9 (excluding 3.9.1), managed with Poetry.

## Commands

```bash
poetry install                          # install deps (dev group included)
poetry run pytest                       # run full test suite (unit tests only; e2e excluded)
poetry run pytest tests/core/service/message/message_service_test.py::TestClass::test_method  # single test
poetry run pytest -m e2e --no-cov       # run e2e tests (separate marker, needs real Symphony env)
poetry run ruff check symphony examples # lint
poetry run ruff format symphony examples # format
poetry run pylint <module_name>         # legacy lint (still configured via .pylintrc)
cd docsrc && make html                  # build Sphinx docs locally
poetry build                            # build package
```

Tests use `pytest-asyncio` — async test functions are marked with `@pytest.mark.asyncio`. Coverage config excludes `symphony/bdk/gen/*` and enforces `fail_under = 90.0` (see `pyproject.toml`). Ruff excludes `symphony/bdk/gen` (generated code, not linted/formatted). Pre-commit hooks run `ruff format` + `ruff check --fix` (`.pre-commit-config.yaml`).

## Architecture

### Generated vs. hand-written code

`symphony/bdk/gen/` (~440 files) is **generated** from the Symphony OpenAPI spec via `openapi-generator` (fork at `SymphonyPlatformSolutions/openapi-generator`) — never edit it by hand. It contains low-level API/model classes split by API family: `agent_api`/`agent_model`, `auth_api`/`auth_model`, `pod_api`/`pod_model`, `login_api`/`login_model`, `group_api`/`group_model`. To regenerate: build the generator JAR (see `api_client_generation/`), then run `api_client_generation/generate.sh`. This is a rare, deliberate operation, not something to do incidentally.

Everything under `symphony/bdk/core/` and `symphony/bdk/ext/` is hand-written, higher-level BDK code that wraps the generated clients.

### Entry point and service wiring

`symphony.bdk.core.symphony_bdk.SymphonyBdk` is the single entry point (usable as an async context manager). Constructing it with a `BdkConfig` wires up:
- `ApiClientFactory` (`core/client/api_client_factory.py`) — builds the low-level pod/agent API clients from config.
- `AuthenticatorFactory` (`core/auth/`) — builds bot / OBO / extension-app authenticators; produces `AuthSession`/`OboAuthSession`.
- `ServiceFactory` (`core/service_factory.py`) — lazily builds all domain services (message, stream, user, connection, application, signal, session, presence, health, datafeed/datahose loops) from the api client factory + bot session.

Bot services are only initialized if `config.bot.is_authentication_configured()`; otherwise only OBO (on-behalf-of) flows via app authentication are available. Public accessor methods on `SymphonyBdk` (`.messages()`, `.streams()`, `.datafeed()`, etc.) are guarded by the `@bot_service` decorator, which raises `BotNotConfiguredError` if the bot isn't configured; app-scoped accessors (`.app_authenticator()`, `.obo()`, `.obo_services()`) use `@app_service` and raise `BdkConfigError` instead.

### Config

`core/config/loader.py` (`BdkConfigLoader`) loads a `BdkConfig` (`core/config/model/`) from a file path, raw YAML/JSON string, or the `$HOME/.symphony/` convention directory — the latter is the standard place to keep credentials/config out of the repo.

### Activities and datafeed

Bots react to events via the datafeed loop (`core/service/datafeed/` — v1 and v2 implementations, plus `datahose_loop.py` for the datahose alternative) which pushes real-time events to subscribers implementing `RealTimeEventListener`. `ActivityRegistry` (`core/activity/registry.py`) subscribes to the datafeed loop and dispatches to registered activities (slash `command.py`, `form.py` for elements/forms, `user_joined_room.py`). This registry is only created when bot services are initialized.

### Auth model

Three authentication flows live under `core/auth/`: bot (service account, RSA or shared-secret via `bot_authenticator.py`), OBO (`obo_authenticator.py`, acting as a user through an extension app), and extension app auth (`ext_app_authenticator.py`, JWT-based via `jwt_helper.py`). `TokensRepository` handles cached session/key-manager tokens.

### Extensions

`core/extension.py` (`ExtensionService`) plus `symphony/bdk/ext/` provide the extension mechanism for optional/pluggable BDK modules (e.g. `ext/group.py`).

### Retry

`core/retry/` wraps `tenacity` to provide the BDK's async retry strategy for API calls (network failures, rate limiting).

## Tests

Test tree under `tests/` mirrors `symphony/bdk/` package structure 1:1 (e.g. `symphony/bdk/core/service/message/` → `tests/core/service/message/`). Fixtures/sample payloads live in `tests/resources/`, grouped by domain (`message_response/`, `session/`, `stream/`, etc.).

## Examples

`examples/` contains runnable snippets per feature area (`authentication/`, `datafeed/`, `activities/`, `services/`, `extension/`, `multiple_instances/`) — useful as reference for intended usage patterns when implementing or modifying core features.
