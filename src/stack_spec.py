"""
stack_spec.py -- U25 / S1 of the CONDITIONAL STACK format, adopted at the
September 13th ~9:00 pm CT staff meeting (disposition MODIFY, ten binding rules;
record research/infrastructure/staff-meeting-conditional-stack-2026-09-13.md).

WHAT A STACK IS (plain English):
A flat hypothesis is one market state, bucketed, against one forward outcome.
A conditional stack is 2-3 layers evaluated in a FIXED order --

    context   (a regime known before the session, or before the location forms)
    location  (where price sits inside a structure, known before the trigger)
    trigger   (the deterministic event that fires the entry)

-- pre-registered as ONE hypothesis, frozen as a whole, costing ONE trial
(a PAIRED family costs two). This module is the schema, the validator, and the
hash. It deliberately contains NO scanning logic: a spec must be expressible,
checkable and hashable before any data is touched.

THE TWO THINGS THIS FILE EXISTS TO PREVENT
1. LAYER SHOPPING. Three layers with five candidate variables each is 125
   stacks; test them all, report the winner, and 125 trials were spent while
   one was registered. Guard: spec_hash() over the canonical JSON of the WHOLE
   spec. The hash is written into the registry BEFORE the runner may execute.
   Change any layer, edge, window, horizon, exit or cost assumption and the hash
   changes -- which makes it a different trial, by construction, not by promise.
2. OUT-OF-TIME LAYERS. A layer that is only known after the trigger fires makes
   the stack circular (the TIMING RULE, src/idea_factory.py KNOWN_AT). Guard:
   validate() refuses any spec whose layers are not strictly ordered in time
   ahead of the trigger.

Rule 1 of the ten also lives here: the 2-layer ceiling holds until the format
has produced ONE result. FORMAT_HAS_RESULT is flipped (with a dated comment)
only when the first stack closes with adequate power, and only then does
validate() admit a third layer.

Time convention: `known_at` is minutes from local midnight in the session's
exchange timezone (America/New_York), the same convention as
src/idea_factory.py KNOWN_AT -- e.g. prior close = -480, 09:30 = 570,
10:00 = 600. A negative value means "known before the session opened".
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

# Flipped ONLY when the first stack closes with adequate power. Rule 1.
FORMAT_HAS_RESULT = True           # 2026-09-13 ~9:12 pm CT: Stack A closed as a POWERED null
                                   # (hyp-000161). The format has produced one result, so rule 1
                                   # now admits a third layer. One more powered null closes the
                                   # format entirely (rule 10).
MAX_LAYERS_BEFORE_FIRST_RESULT = 2
MAX_LAYERS_AFTER_FIRST_RESULT = 3
DEFAULT_FLOOR_OCCURRENCES = 100    # Rule 4 default; Statistical may raise it, never lower it

ROLE_ORDER = ("context", "location", "trigger")
REQUIRED_TOP = ("stack_id", "family", "layers", "outcome", "horizon", "exit",
                "cost_model", "floor_occurrences", "mde", "paired", "data_slice",
                "mechanism_doc", "look_cells_k")
REQUIRED_LAYER = ("role", "variable", "edges", "known_at", "mechanism")


class StackSpecError(ValueError):
    """Raised when a spec is not admissible. The message lists every reason."""


def _fail(reasons: list[str]) -> None:
    if reasons:
        raise StackSpecError("stack spec rejected:\n  - " + "\n  - ".join(reasons))


def validate(spec: dict[str, Any], *, format_has_result: bool | None = None) -> dict:
    """Checks a spec against the ten binding rules this module can mechanically
    check. Returns the spec unchanged; raises StackSpecError listing EVERY
    problem found (not just the first), so a spec is fixed in one pass."""
    has_result = FORMAT_HAS_RESULT if format_has_result is None else format_has_result
    r: list[str] = []

    for k in REQUIRED_TOP:
        if k not in spec:
            r.append(f"missing required field '{k}'")
    layers = spec.get("layers")
    if not isinstance(layers, list) or not layers:
        _fail(r + ["'layers' must be a non-empty list"])

    ceiling = MAX_LAYERS_AFTER_FIRST_RESULT if has_result else MAX_LAYERS_BEFORE_FIRST_RESULT
    if len(layers) > ceiling:
        r.append(f"{len(layers)} layers, ceiling is {ceiling} "
                 f"({'format has a result' if has_result else 'format has produced no result yet -- rule 1'})")
    if len(layers) < 2:
        r.append("a stack needs at least 2 layers; 1 layer is a flat hypothesis, register it as one")

    roles = [l.get("role") for l in layers]
    if roles[-1] != "trigger":
        r.append("the last layer must be the trigger")
    if roles.count("trigger") != 1:
        r.append("exactly one trigger layer is required")
    for l in layers:
        for k in REQUIRED_LAYER:
            if k not in l:
                r.append(f"layer {l.get('role') or '?'}: missing '{k}'")
        if l.get("role") not in ROLE_ORDER:
            r.append(f"layer role '{l.get('role')}' is not one of {ROLE_ORDER}")
        if not str(l.get("mechanism") or "").strip():
            r.append(f"layer {l.get('role')}: every layer needs its own mechanism (rule 5)")
    # role order must follow context -> location -> trigger
    seen = [ROLE_ORDER.index(x) for x in roles if x in ROLE_ORDER]
    if seen != sorted(seen):
        r.append(f"layers out of role order: {roles} (context before location before trigger)")

    # TIMING RULE, per layer: strictly increasing known_at, all strictly before
    # the trigger's own window start.
    try:
        kn = [int(l["known_at"]) for l in layers]
    except Exception:
        kn = []
        r.append("every layer needs an integer 'known_at' (minutes from local midnight, ET)")
    if kn:
        for a, b, la, lb in zip(kn, kn[1:], layers, layers[1:]):
            if a >= b:
                r.append(f"'{la.get('role')}' known_at {a} is not before '{lb.get('role')}' known_at {b} "
                         f"(timing rule, rule 6)")
        tw = spec.get("trigger_window_start")
        if tw is not None and any(k >= int(tw) for k in kn[:-1]):
            r.append(f"a non-trigger layer is known at or after the trigger window start {tw} (rule 6)")

    if not str(spec.get("mechanism_doc") or "").strip():
        r.append("mechanism_doc path is required -- the doc is written BEFORE the scan")
    if not str(spec.get("interaction_claim") or "").strip():
        r.append("interaction_claim is required: why the layers TOGETHER mean something they do not "
                 "separately. 'It filters out losers' is not a mechanism (rule 5)")
    floor = spec.get("floor_occurrences")
    if not isinstance(floor, int) or floor < DEFAULT_FLOOR_OCCURRENCES:
        r.append(f"floor_occurrences must be an integer >= {DEFAULT_FLOOR_OCCURRENCES} "
                 f"(rule 4; Statistical may raise it, never lower it)")
    if not str(spec.get("mde") or "").strip():
        r.append("mde (minimum detectable effect at the floor) must be stated BEFORE the scan (rule 4)")
    if spec.get("paired") is not True:
        r.append("the first test of any stack is paired: trigger alone vs trigger inside context (rule 2)")
    if spec.get("data_slice") != "discovery":
        r.append("stacks are registered and first run on the Discovery slice only")
    if not isinstance(spec.get("look_cells_k"), int) or spec["look_cells_k"] < 0:
        r.append("look_cells_k (how many interaction cells were LOOKED at before this spec) is required "
                 "disclosure for the blind packet (rule 7)")
    _fail(r)
    return spec


def canonical(spec: dict[str, Any]) -> str:
    """The exact bytes the hash is taken over: sorted keys, no insignificant
    whitespace. Anything not in the spec is not in the hash -- and anything in
    the spec, including a comment field, changes it."""
    return json.dumps(spec, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def spec_hash(spec: dict[str, Any]) -> str:
    return hashlib.sha256(canonical(spec).encode("utf-8")).hexdigest()


def trials_cost(spec: dict[str, Any]) -> int:
    """One stack = one trial; a paired family = two (rule 2 makes paired the
    default for a first test, so this is 2 in practice)."""
    return 2 if spec.get("paired") else 1


def cells(spec: dict[str, Any]) -> int:
    """Pre-registered cells this stack will evaluate -- what goes into
    SCAN_REGISTRY['cells_scanned'] and therefore into the project-wide
    Discovery trial count."""
    return int(spec.get("pre_registered_cells") or trials_cost(spec))


def summary(spec: dict[str, Any]) -> str:
    ls = " -> ".join(f"{l['role']}:{l['variable']}[{l['edges']}]" for l in spec["layers"])
    return (f"{spec['stack_id']} | {ls} | outcome={spec['outcome']} horizon={spec['horizon']} "
            f"| floor={spec['floor_occurrences']} paired={bool(spec.get('paired'))} "
            f"| hash={spec_hash(spec)[:12]}")


if __name__ == "__main__":
    import sys
    with open(sys.argv[1]) as fh:
        s = json.load(fh)
    validate(s)
    print(summary(s))
    print("full sha256:", spec_hash(s))
