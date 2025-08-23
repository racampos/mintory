# Agent Specifications (Typed IO + Acceptance)

## Lore Agent

- Input: `{ date_label }`
- Output: `LorePack` = { summary_md (<=200 words), bullet_facts[5..10], sources[>=5], prompt_seed }
- Acceptance:
  - `summary_md` non-empty, word count <= 200.
  - `sources` use http(s) URLs (do not fetch in backend for demo).
  - `prompt_seed.style` and `.palette` non-empty.

## Artist Agent

- Input: `LorePack`
- Output: `ArtSet` with 4–6 `cids`, `thumbnails`, `style_notes`.
- Acceptance:
  - 4 ≤ `cids.length` ≤ 6, each unique.
  - Validate CID format (`ipfs://...`).
  - Thumbnails <= 200KB.

## Vote Agent

- Input: `ArtSet`, `VoteConfig`
- Output: `VoteResult` with `winner_cid`, `tally`.
- Acceptance:
  - Timeout respected; if no votes, pick index 0 and record `fallback: true`.
  - Emit events for open, cast, close.

## Mint Agent

- Input: `{ LorePack, winner_cid }`
- Output: `MintReceipt` = { tx_hash, token_id, token_uri }
- Acceptance:
  - tokenURI resolves to the pinned JSON.

## Attestation Agent (optional)

- Input: `{ token_id, winner_cid, statement_uri }`
- Output: `AttestationReceipt` = { id, uri }
- Acceptance:
  - `uri` is retrievable (IPFS CID format).

## Guard Agent (stub)

- Always returns `PolicyOK` unless `summary_md` contains disallowed words (configurable list).

