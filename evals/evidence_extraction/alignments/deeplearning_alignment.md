# Deep Learning Evidence Extraction — Provisional Alignment

**Review status:** HUMAN_REVIEWED (author-confirmed for Portfolio V1; historical analysis preserved).

## Gold-to-Agent review

| Gold | Agent | Label | Why |
|---|---|---|---|
| G001 | — | MISSING | Classical ML implementation omitted |
| G002 | E002 | MATCH | NN-from-scratch implementation captured |
| G003 | E005 | PARTIAL_MATCH | Test accuracy captured; training accuracy omitted |
| G004 | E003 | MATCH | Optimization implementation captured |
| G005 | E006 | PARTIAL_MATCH | Test accuracy captured; training accuracy omitted |
| G006 | E004 | PARTIAL_MATCH | CNN bundled with GAN/DANN; implementation detail lost |
| G007 | E007 | PARTIAL_MATCH | Test accuracy captured; training accuracy omitted |
| G008 | E004 | PARTIAL_MATCH | GAN bundled with CNN/DANN; training/loss detail lost |
| G009 | — | MISSING | GAN qualitative evaluation omitted |
| G010 | E004 | PARTIAL_MATCH | DANN bundled; gradient reversal/domain-adaptation detail lost |
| G011 | E008 | MATCH | DANN target-domain improvement captured |
| G012 | — | MISSING | Engineering workflow omitted |

## Agent-only

- **E001 — EXTRA_OUT_OF_SCOPE:** repository contains six projects. Grounded, but not useful candidate evidence under the current benchmark policy.

## Why there is no single score yet

One Agent unit (E004) bundles three distinct capabilities, so a binary one-to-one precision/recall calculation would hide the granularity problem. We should freeze how `PARTIAL_MATCH` is scored before producing a final metric.