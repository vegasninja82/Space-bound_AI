# SPACE_BOUND_AI — Test Report

## Test Files Discovered

| # | File | Test Count |
|---|------|-----------|
| 1 | tests/test_api.py | 8 |
| 2 | tests/test_core_additional.py | 24 |
| 3 | tests/test_engine.py | 15 |
| | **Total** | **47** |

## Every Test Function

### tests/test_api.py (8 tests)

| # | Function | Category |
|---|----------|----------|
| 1 | `test_health` | API |
| 2 | `test_providers` | API |
| 3 | `test_tracks` | API |
| 4 | `test_config` | API |
| 5 | `test_chat_empty_prompt` | API / Error Handling |
| 6 | `test_chat_mock` | API / Engine |
| 7 | `test_chat_default_provider` | API / Adapters |
| 8 | `test_metrics` | API / Metrics |

### tests/test_core_additional.py (24 tests)

| # | Function | Category |
|---|----------|----------|
| 1 | `test_validator_empty_answer` | Validator |
| 2 | `test_validator_normal_answer` | Validator |
| 3 | `test_validator_contains_metrics` | Validator |
| 4 | `test_merge_empty_results` | Merge / Error Handling |
| 5 | `test_merge_direct_priority` | Merge |
| 6 | `test_merge_source_tracking` | Merge |
| 7 | `test_scheduler_returns_tracks` | Scheduler |
| 8 | `test_scheduler_direct_exists` | Scheduler |
| 9 | `test_scheduler_validation_exists` | Scheduler |
| 10 | `test_adapter_generate_multiple` | Adapters |
| 11 | `test_adapter_health_boolean` | Adapters |
| 12 | `test_adapter_usage_structure` | Adapters |
| 13 | `test_registry_mock_provider` | Adapters |
| 14 | `test_registry_unknown_provider` | Adapters / Error Handling |
| 15 | `test_baseline_metadata` | Engine / Baseline |
| 16 | `test_baseline_request_storage` | Engine / Baseline |
| 17 | `test_engine_returns_validation` | Engine |
| 18 | `test_engine_returns_timing` | Engine |
| 19 | `test_engine_returns_answer` | Engine |
| 20 | `test_engine_track_execution` | Engine / Concurrency |
| 21 | `test_mock_provider_is_deterministic` | Adapters / Regression |
| 22 | `test_config_object_exists` | Config / Regression |
| 23 | `test_logger_exists` | Regression |
| 24 | `test_engine_object_exists` | Regression |

### tests/test_engine.py (15 tests)

| # | Function | Category |
|---|----------|----------|
| 1 | `test_config_loads` | Config |
| 2 | `test_mock_adapter_generate` | Adapters |
| 3 | `test_mock_adapter_health` | Adapters |
| 4 | `test_mock_adapter_token_usage` | Adapters |
| 5 | `test_registry_fallback` | Adapters / Error Handling |
| 6 | `test_registry_get_mock` | Adapters |
| 7 | `test_baseline_builder` | Engine / Baseline |
| 8 | `test_scheduler` | Scheduler |
| 9 | `test_merge_engine_prefers_direct` | Merge |
| 10 | `test_merge_engine_fallback_to_perspective` | Merge |
| 11 | `test_merge_engine_fallback_to_first` | Merge |
| 12 | `test_validator_passes` | Validator |
| 13 | `test_engine_run` | Engine / Concurrency |
| 14 | `test_engine_run_track` | Engine / Concurrency |
| 15 | `test_engine_validation_structure` | Engine / Validator |

## Total Tests Discovered: 47

## Categories Covered

| Category | Tests | Count |
|----------|-------|-------|
| Engine | test_engine_returns_validation, test_engine_returns_timing, test_engine_returns_answer, test_engine_track_execution, test_engine_run, test_engine_run_track, test_engine_validation_structure, test_baseline_metadata, test_baseline_request_storage, test_baseline_builder | 10 |
| Scheduler | test_scheduler_returns_tracks, test_scheduler_direct_exists, test_scheduler_validation_exists, test_scheduler | 4 |
| Validator | test_validator_empty_answer, test_validator_normal_answer, test_validator_contains_metrics, test_validator_passes | 4 |
| Merge | test_merge_empty_results, test_merge_direct_priority, test_merge_source_tracking, test_merge_engine_prefers_direct, test_merge_engine_fallback_to_perspective, test_merge_engine_fallback_to_first | 6 |
| Adapters | test_adapter_generate_multiple, test_adapter_health_boolean, test_adapter_usage_structure, test_registry_mock_provider, test_registry_unknown_provider, test_mock_adapter_generate, test_mock_adapter_health, test_mock_adapter_token_usage, test_registry_fallback, test_registry_get_mock, test_mock_provider_is_deterministic, test_chat_default_provider | 12 |
| API | test_health, test_providers, test_tracks, test_config, test_chat_empty_prompt, test_chat_mock, test_metrics | 7 |
| Metrics | test_metrics | 1 |
| Storage | (covered indirectly via test_metrics and test_engine_run which exercise SQLite) | 2 |
| Error Handling | test_chat_empty_prompt, test_merge_empty_results, test_registry_unknown_provider, test_registry_fallback | 4 |
| Concurrency | test_engine_run, test_engine_run_track, test_engine_track_execution | 3 |
| Config | test_config_loads, test_config_object_exists | 2 |
| Regression | test_mock_provider_is_deterministic, test_config_object_exists, test_logger_exists, test_engine_object_exists | 4 |

## 69-Test Suite Status

The repository does NOT contain 69 tests. The current test count is **47 tests** across 3 test files. The 69-test suite was not found in any commit in the repository's git history. The current 47 tests represent the complete test suite that exists in the repository.
