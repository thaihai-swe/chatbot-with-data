# Debugging Checklist

Use this when the investigation is about a failure, regression, or uncertain current behavior.

## Reproduction

- What exact symptom is being reported?
- Can it be reproduced now?
- If not, what evidence still makes the failure credible?

## Boundary Trace

- Where does the wrong behavior first become visible?
- Which upstream boundary was checked next?
- Which boundary still behaves as expected?

## Root-Cause Confidence

- What is established fact?
- What is still inference?
- What single next check would most reduce uncertainty?

## Brownfield Safety

- What unchanged behavior must the repair preserve?
- Which existing tests, logs, or integration seams are the safest proof points?
