# Question
What remains undocumented or weakly documented about the KB build pipeline and SlimyAI login/session flow?

# Answer
The two new canonical articles close most high-value structure gaps, but several implementation-level gaps remain.

## Remaining KB Pipeline Gaps
1. Canonical branch/remote remediation is still weakly documented.
- The pipeline now documents `kb-sync.sh` as `origin/main`-locked and fail-open, including observed `remote ref main` failure behavior, but there is no explicit recovery runbook for clones tracking a different default branch. (Citation: [Knowledge Base Build Pipeline](../wiki/architecture/knowledge-base-build-pipeline.md))

2. Automation boundary is documented, but no operator checklist exists for consistency enforcement.
- The article states compile/index/stale maintenance is manual, with helper scripts only, but there is no required acceptance checklist for “compile complete” quality gates. (Citation: [Knowledge Base Build Pipeline](../wiki/architecture/knowledge-base-build-pipeline.md), [Session Closeout Pattern](../wiki/patterns/session-closeout-pattern.md))

3. Query-to-wiki promotion criteria remain policy-light.
- The loop is defined (query in `output/`, file-back into `wiki/`), but thresholds for when output must be promoted are still judgment-based and not formalized. (Citation: [Knowledge Base Build Pipeline](../wiki/architecture/knowledge-base-build-pipeline.md))

## Remaining Login/Session Gaps
1. Verification-link route wiring is unresolved.
- Registration email currently references `/auth/verify?token=...`, while verified handler implementation is `/api/session/verify?token=...`, and no `app/auth/verify/page.tsx` route is present in this repo snapshot. Final production behavior is therefore not fully proven from code/docs. (Citation: [SlimyAI Login and Session Flow](../wiki/architecture/slimyai-login-and-session-flow.md))

2. Local-auth coexistence policy is still weakly documented.
- The canonical flow is DB-backed `SlimySession`, but `/api/local-auth/*` testing endpoints still exist. The deprecation/removal policy and runtime exposure expectations are not fully specified. (Citation: [SlimyAI Login and Session Flow](../wiki/architecture/slimyai-login-and-session-flow.md), [Auth and Retired Services](../wiki/architecture/auth-and-retired-services.md))

3. Owner allowlist status is only partially resolved.
- Owner route enforcement is role/`OWNER_USER_ID` based, while allowlist structures still exist in schema/tests. The intended long-term role of allowlist bootstrap in active auth is not fully pinned down in architecture docs. (Citation: [SlimyAI Login and Session Flow](../wiki/architecture/slimyai-login-and-session-flow.md))

4. Session lifecycle edge behavior is still thin.
- Core create/validate/revoke/reset behavior is documented, but there is no explicit architecture note for session rotation/renewal strategy, concurrent session policy, or cleanup/retention tasks for expired rows. (Citation: [SlimyAI Login and Session Flow](../wiki/architecture/slimyai-login-and-session-flow.md))

## Confidence Level
High for the identified gaps above, because each item is directly tied to either a documented “unknown/legacy” marker or an explicitly absent operational policy in current wiki coverage.

## Wiki Gaps
- Add a short “KB Sync Failure Runbook” section (or standalone troubleshooting page) for branch mismatch and remote-ref failures.
- Add an “Auth Verification Routing” note once `/auth/verify` vs `/api/session/verify` production routing is confirmed.
- Add a concise “Auth Legacy Surface Policy” section defining expected lifecycle for `/api/local-auth/*`.
