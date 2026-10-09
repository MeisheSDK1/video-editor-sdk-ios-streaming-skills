# Module Contract Schema

## Levels

| Level | Purpose |
|---|---|
| `api_brick` | Atomic public SDK object or operation |
| `api_recipe` | Ordered API sequence that creates usable state |
| `small_module` | Reusable or user-visible feature |
| `big_module` | Product workflow composed from smaller modules |
| `app_blueprint` | Complete application shell and default module set |

## Fields

Every registry item uses stable `id`, `title`, `level`, `priority`, `category`, `aliases`, `requires`, and `provides`. Modules additionally declare `api_recipes`, `simple_code_ids`, `render_units`, `public_api_bindings`, `official_doc_routes`, `info_plist`, `xcode`, `resource_contract`, `navigation`, `host_contract`, `resources`, `privacy_usage_descriptions`, `template_features`, `guards`, `conflicts`, `lifecycle`, `integration_modes`, and `verification_state` as applicable. Use `capability_states` when one module contains capabilities with different evidence levels, and use `scope_boundary` on a recipe when its bundled code unit covers only part of the documented contract.

## Composition Rules

1. Resolve hard dependencies recursively and topologically.
2. Select at most one application template.
3. Add optional modules only when requested, selected by a blueprint, or required downstream.
4. Packaged-material modules require `asset-package-service` and matching resource keys.
5. Incremental mode stages transactionally and does not overwrite host conflicts.
6. API-only mode emits no product shell.
7. Bind exact API requests through `api_signatures` and expand only predecessor units.
8. Do not render `contract_only` units.
9. Timeline creation precedes clip insertion; output connection precedes playback; conflicting engine state stops before mutation, removal, or compile.

## Code Unit States

- `contract_only`
- `objc_compiled_unit`
- `swift_compiled_unit`
- `generated_module`
- `runtime_verified`

Runtime state is never inferred from another state.
