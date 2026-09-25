## Problem

What flight-computer behavior, failure mode, requirement, or maintenance need does this address?

## Approach

What changed, and why is this the right approach for the payload?

Call out important timing, power, I/O, hardware, recovery, or configuration decisions when relevant.

## Verification

### Automated

List the checks and tests you ran.

### Hardware

Select the strongest level completed and describe the observed result.

- [ ] CI or simulated hardware only
- [ ] Raspberry Pi
- [ ] Bench hardware
- [ ] Integrated payload hardware
- [ ] Not applicable

### Measured results

Include timing, power, packet rate, sensor accuracy, memory, or other measurements when the change makes a measurable claim.

## Risks and limitations

What remains unverified, hardware-dependent, timing-sensitive, or intentionally out of scope?

Do not describe behavior as flight-ready unless that level of validation was actually completed.

## References

Link requirements, component datasheets, protocols, hardware documentation, prior issues, or test notes that support the design or evidence.

## Checklist

- [ ] The change is focused on one task.
- [ ] Tests were added or updated when behavior changed.
- [ ] Evidence supports the behavior being claimed.
- [ ] Units and test conditions are stated for measurements.
- [ ] No credentials or private telemetry were committed.
- [ ] Documentation changed when setup or operations changed.
