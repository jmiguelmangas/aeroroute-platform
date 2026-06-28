# aeroroute-platform

The authoritative architecture and implementation guide is
[`docs/HLD.md`](docs/HLD.md), currently Version 6.0. Copies outside this
repository are exports and must be regenerated from that source.

Platform composition, local development, integration testing, observability,
and release manifests for AeroRoute MLX. It owns no product business logic.

> AeroRoute MLX generates an educational pre-operational flight-plan
> simulation. Results are approximate, may use incomplete public data, are not
> an ICAO-fileable flight plan, and are not suitable for operational or
> safety-critical decisions.

## Commands

Run `make bootstrap` once, then `make check` for repository-local validation.
`make dev-up`, `make dev-down`, `make integration`, `make e2e`, and
`make release-verify` compose the released sibling artifacts.
