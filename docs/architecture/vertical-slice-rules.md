# Vertical Slice Rules

Vertical slices are self-contained feature modules that include UI, APIs, data access, and supporting assets. They minimize coupling and improve replaceability.

## Core Principles

- **Isolation:** A slice owns its logic and data flow. Avoid shared mutable state or hidden dependencies.
- **Contracts First:** Each slice publishes a `schema.json` describing its public interface. Changes should be versioned and reviewed.
- **Independent Evolution:** Slices should be easy to develop, test, and deploy with minimal coordination.
- **Composition at the Edges:** Application shells compose slices through their public entry points and routers rather than internal details.

## Forbidden Patterns

- Shared business services that live outside slices but are imported across them.
- Direct imports between slices for business logic or stateful helpers.
- Cross-slice data writes or shared mutable state (databases, caches, in-memory singletons).
- Sneaking coupling through test helpers, fixtures, or code generation without contracts.

## Allowed Communication Patterns

- Public API contracts declared in `slice.schema.json` (HTTP, RPC, or message events).
- UI composition through published entry points (e.g., `index.ts` exports) without reaching into internal folders.
- Read-only data projections via dependency declarations that pin another slice's contract version.
- Shared platform services that are explicitly designated and versioned (logging, configuration, tracing).

## Examples

- ✅ A frontend slice renders another slice's public component via its documented export.
- ✅ A backend slice queries another slice's read-only endpoint using the version pinned in its dependencies.
- ❌ A slice imports another slice's utility module from an `internal` folder.
- ❌ Two slices share a mutable singleton service for caching or state sharing.
