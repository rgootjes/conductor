# Vertical Slice Rules

Vertical slices are self-contained feature modules that include UI, APIs, data access, and supporting assets. They minimize coupling and improve replaceability.

## Core Principles

- **Isolation:** A slice owns its logic and data flow. Avoid shared mutable state or hidden dependencies.
- **Contracts First:** Each slice publishes a `schema.json` describing its public interface. Changes should be versioned and reviewed.
- **Independent Evolution:** Slices should be easy to develop, test, and deploy with minimal coordination.
- **Composition at the Edges:** Application shells compose slices through their public entry points and routers rather than internal details.

## Allowed Sharing

- Platform-level utilities (logging, configuration, tracing) that are explicitly designated as shared.
- Schema-driven data contracts that are versioned and validated.

## Prohibited Coupling

- Direct imports between slices for business logic.
- Reliance on unversioned shared globals or implicit side effects.
