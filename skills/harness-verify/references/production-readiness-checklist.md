# Production Readiness Checklist

<!-- Used by /harness-verify before production deployments. Covers observability, security, performance, rollback, and operational readiness. -->

## Purpose

Verify that a feature is not just functionally correct but operationally ready for production. Run this checklist for any High or Critical risk deployment.

## Checklist

### Functional Readiness

- [ ] All mechanical gate commands pass (tests, lint, typecheck)
- [ ] Alignment audit shows no drift from spec
- [ ] All acceptance criteria have fresh verification evidence
- [ ] No open blockers in tasks.md
- [ ] Feature works in a production-like environment (not just local)

### Observability

- [ ] Key operations emit structured logs
- [ ] Error paths log sufficient context for debugging
- [ ] Metrics are emitted for critical paths (latency, error rate, throughput)
- [ ] Alerts are configured for failure conditions
- [ ] Dashboard updated to include new feature metrics
- [ ] Tracing spans cover the request path

### Security

- [ ] Authentication and authorization enforced on new endpoints
- [ ] Input validation on all external-facing inputs
- [ ] No secrets hardcoded (all from environment/vault)
- [ ] SQL injection / XSS / CSRF protections in place
- [ ] Rate limiting on public endpoints
- [ ] Sensitive data not logged or exposed in error messages

### Performance

- [ ] Response time within budget (check `docs/project/project-constraints.md`)
- [ ] No N+1 queries or unbounded loops
- [ ] Database queries have appropriate indexes
- [ ] Caching strategy implemented where needed
- [ ] Load tested at expected peak (if applicable)
- [ ] Memory usage stable under load (no leaks)

### Data

- [ ] Database migrations are reversible
- [ ] Migrations tested against production-scale data
- [ ] Backfill strategy defined (if applicable)
- [ ] Data validation at ingestion boundaries
- [ ] No data loss on failure (transactions, idempotency)

### Rollback

- [ ] Deployment is reversible (can roll back to previous version)
- [ ] Feature flag available for gradual rollout (if applicable)
- [ ] Rollback procedure documented
- [ ] Rollback tested or verified possible
- [ ] Database changes are backward-compatible with previous code version

### Operational

- [ ] Runbook updated for new failure modes
- [ ] On-call team aware of the deployment
- [ ] Deployment window chosen (avoid high-traffic periods)
- [ ] Monitoring in place before deployment (not after)
- [ ] Communication plan for user-facing changes

### Documentation

- [ ] API documentation updated (if applicable)
- [ ] Architecture doc updated (if boundaries changed)
- [ ] Changelog entry written
- [ ] Internal team notified of behavioral changes

## Verdict

| Category | Status | Notes |
|----------|--------|-------|
| Functional | [Pass \| Fail] | |
| Observability | [Pass \| Fail] | |
| Security | [Pass \| Fail] | |
| Performance | [Pass \| Fail] | |
| Data | [Pass \| Fail \| N/A] | |
| Rollback | [Pass \| Fail] | |
| Operational | [Pass \| Fail] | |
| Documentation | [Pass \| Fail] | |

**Overall:** [Ready for Production | Blocked — see notes]

## When to Use

- All deployments that the active feature profile classifies as `High` or `Critical`
- Any deployment touching auth, payments, or user data
- First deployment of a new service or major feature
- Optional for Low/Medium risk (use judgment)
