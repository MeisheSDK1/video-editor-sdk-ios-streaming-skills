# Standalone Workflow

## Retrieval Order

1. Search `skill-lookup-index.json` with `scripts/search_skill_index.py`.
2. For applications or broad features, resolve dependency closure with `scripts/compose_modules.py`.
3. Read only the routed class-family, constraint, resource, and project references.
4. Bind exact Objective-C selectors through `sdk-signature-map.json`, then use only compile-verified imported Swift names for Swift output.
5. Render only code units allowed by `simple-code-registry.json`.
6. Reconcile the plan with emitted source, target membership, Build Phases, copied resources, callable entries, error states, and cleanup.
7. Validate structure and public symbols before claiming implementation completeness.

## Output Modes

- `new-app`: create one UIKit product shell and dependency-closed modules; default generated source is Swift unless the caller explicitly selects Objective-C.
- `incremental`: stage an additive transaction for an existing host; apply only with `--apply`.
- `api-only`: emit controllers, a concrete usage sample, resource contracts, and a patch manifest without a product shell.

## Generation Truthfulness

A plan is not implementation evidence. A module may be reported as emitted only when its dependency-closed source, required permissions and resources, target membership, callable integration entry, observable failure states, and cleanup are present in the output. Report placeholder and `contract_only` output explicitly.

When the caller supplies `--framework` or `--license`, copy only those inputs into the generated app. Embed and sign the dynamic framework. Copy the license under a stable resource name and add it to the target Resources phase. Do not persist the source path in reusable skill data.

## Evidence Boundary

Public headers prove signatures. Official documentation explains semantics. Typechecking proves a source unit is accepted by the compiler against supplied headers. Xcode build proves only the selected build. Device and visual behavior require their own recorded evidence.

## Prohibited Dependencies

Normal use must not require original analysis inputs, non-bundled local source trees, local documentation trees, private services, or SDK release-specific paths. The generated skill and its maintenance data remain release-neutral.
