# Local Inference
> Category: concepts
> Sources: raw/research/nuc1-ollama-models.md, raw/decisions/nuc1-running-services.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

Local inference is the pattern of running LLM serving on-host (Ollama on NUC1) and consuming it through explicit local or tunneled channels instead of external API calls.

## Runtime Profile
- Ollama listens on loopback `127.0.0.1:11434`, which keeps it private by default.
- Model inventory currently includes lightweight and mid-size options suitable for safety-first or fallback workflows.
- Service locality means model use is tied to host capacity and process scheduling on NUC1.

## Operational Implications
- Cross-host usage requires explicit transport (for example SSH port-forward), not direct remote exposure.
- Availability is primarily an ops concern (runtime up, models present), not an API key concern.
- Model naming/version drift should be treated as a runtime compatibility check before automation jobs are enabled.

## See Also
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
- [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md)
- [Truth Gate](truth-gate.md)
