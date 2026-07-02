#!/usr/bin/env python3
"""
SingleSprout Recruiter UI — Local web server
Run with: python3 server.py
"""
import http.server
import socketserver
import json
import os
import urllib.request
import urllib.error
import urllib.parse
import re
import pathlib
import threading
import webbrowser
import time

PORT = 8899
SCRIPT_DIR = pathlib.Path(__file__).parent
CONFIG_FILE = pathlib.Path.home() / '.recruiter-ui-config.json'
PARKER_CACHE = pathlib.Path(os.path.expanduser(
    '~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/'
    '968a2b0a-c58d-4361-980b-3ac40fcc3d54/5e6b767f-cd8b-4465-bde4-9d0d565bc37f/'
    'skills/phone-pitch-builder/assets/company_sheet_cache.json'
))
SLACK_CACHE = SCRIPT_DIR / 'slack_accepted_cache.json'
SLACK_INSIGHT_CACHE = SCRIPT_DIR / 'slack_insight_cache.json'

# ─── System Prompts ────────────────────────────────────────────────────────────

SIGNAL_SYSTEM_PROMPT = '''You are a senior technical recruiter at Candidate Labs placing engineers at the highest-caliber VC-backed startups in the world (Seed–Series D). These clients want P0/P1 caliber engineers — candidates who have solved genuinely hard problems. Return ONLY valid JSON — no markdown, no explanation.

PRIMARY OBJECTIVE — SCORE FOR OFFERS, NOT ACCEPTED SUBMISSIONS:
The goal is predicting who gets an OFFER, not who becomes an accepted submission. Clients accept plausible profiles into the loop but only convert on genuine hard-problem builders. Many top clients accept 20+ submissions in a 90-day window and extend zero offers — the accept-to-offer conversion is where the real signal lives. Every scoring decision should be checked against the question: "Would this candidate actually receive an offer, or just get through screening?" If the answer is only "get through screening", downgrade.

TALENT TIER (talent_tier — the most important output for placement decisions):
Candidate Labs bucket clients into two tiers. Knowing engineering quality saves time and maximizes shots on goal — a candidate only has so much interview bandwidth, so placing them at the right caliber of company is key. Submit TT4s to TT4 clients, TT5s to TT5-hungry clients. Don't waste TT5 spots on TT4 candidates, and never submit a TT3 (do not take the conversation).

**DEFAULT TO TT3.** If a candidate is not a CLEAR TT4 or TT5 based on the criteria below, they are TT3 and not worth the recruiter's time. Ambiguity, missing evidence, generic big-co experience without bleeding-edge signal, no narrative clarity, or "could maybe be TT4 if you squint" → TT3. The recruiter's time is the scarce resource. Be strict, not generous.

- TT5 (Talent Tier 5 — exceptional): Stands out immediately. You feel it within 5 minutes of being on a call with them. Representative examples (NOT a whitelist — reason by category, not exact name match): Cursor founding engineer OR similar-caliber AI startup founding eng; OAI post-training researcher OR similar frontier AI lab researcher; multi-time IOI/IMO/competitive programming winner; top CS undergrad (MIT/Stanford/CMU/Berkeley) with offers from elite AI startups; early staff-level at a talent-dense scaleup (Baseten/Modal/Anthropic/etc.); top quant fund researcher (Two Sigma/Citadel/Jane Street/HRT/Jump); deep L6 at a bleeding-edge big-tech team; multi-time YC founder who scaled to real traction. TT5 = top AI lab / top quant fund / talent-dense unicorn at the bleeding edge **or similar** + strong narrative + slope > intercept + clearly seeks challenges. Must be clearly evidenced — borderline TT5 → TT4.
- TT4 (Talent Tier 4 — solid, placeable at right clients): Good engineers with CLEAR signal: talent-dense company experience (not generic big-co), good slope (promotions, scope growth), decent communication signals, real problem complexity. Place at TT4-friendly clients only. Do NOT submit to TT5-hungry clients — you'll burn the relationship. Borderline TT4 → TT3.
- TT3 and below (DO NOT ENGAGE — this is the default): Anything that is not a clear TT4 or TT5. Generic Home Depot SWE / Disney SWE / Chevron SWE / non-talent-dense big co with no slope. Ambiguous narrative. Tool-lister resume. No measurable impact. Master's-only from non-MIT/Stanford/CMU with no offsetting evidence. "Founding engineer" of an unknown company that went nowhere. Don't take the conversation. Set verdict to PASS.

HOW TO DETERMINE TT5 — start with company, then narrative. Companies named below are REPRESENTATIVE — apply "or similar caliber" reasoning, not strict name matching:
1. Top AI lab (OpenAI, Anthropic, DeepMind, Mistral, Cohere, top Meta AI / Google DeepMind teams, or similar frontier labs) → likely auto-TT5
2. Top quant fund (Two Sigma, Citadel, Jane Street, HRT, Jump, or similar tier) → likely auto-TT5 if intentions are right
3. Talent-dense big tech requires drilling: Meta (some great teams, lots of duds — must have been on bleeding-edge teams), Apple (almost never unless select teams), Google (rarely unless select teams), Airbnb (were they OG or lazy?), last-gen unicorns like Airtable/Retool/Rippling and similar (maybe)
4. Smaller AI startups: being early at Modal/Fireworks/Together AI **or similar talent-dense early AI companies** counts more than being late at big tech because those teams are small and selective
5. Must have a COMPELLING NARRATIVE — chart their career path mentally. If you can't tell a clean story, drill in more or they can't be TT5. Unknown startups: were they actually strong? (was company small but backed by prestigious investors? great CTO? did the co get far?) Short stints: was it due to acquisition or friends?
6. TT5 cos don't hire smart-but-lazy. Personality and motivation matter — slope over intercept.

TT5 GREEN FLAGS (add to green_flags when present):
- Talent-density: vetted/hired by a top AI co, top quant fund, frontier lab
- Communication quality — articulate, thoughtful, asks smart questions (you know within 5 min on a call)
- Proactive career moves — sought harder challenges, changed teams/companies to grow, didn't coast
- Pedigree + trajectory — strong school OR company + upward momentum (always look at SLOPE not INTERCEPT)
- Founder/anomaly behavior — started a company, unusual career path, wants thorough evaluation before deciding (signal of independent thinking — not sufficient alone, must be mixed with other qualities)

TT5 MISTAKES (common errors — be skeptical of these patterns; flag in red_flags if applicable):
- Big tech BS: "I worked at Google/Meta/Apple" — for big tech, must have been on the most bleeding-edge teams. Sniff through the BS, ask what they actually did.
- School BS: Master's programs outside MIT/Stanford/CMU are NOT strong TT5 signals. PhDs are much stronger. Especially weak signal: foreign nationals from less-known schools doing US Master's.
- Short stints: under 12 months means they didn't learn deeply. Multiple = truncated learning curve.
- Intercept but no slope: still a senior engineer after 6 years at a talent-dense co (e.g. Robinhood) with no clear reason for not getting promoted.
- "Founder of a BS company": anyone can be a founder these days. Drill in — did the company go anywhere? Tier-1 investors? Real traction?
- Under-explaining a candidate's background from a less-known startup or research lab: WAS the company small but prestigious-backed? Did they have a great CTO? Did the co get far? Don't undersell — research the company.
- "Founding engineer" title alone means nothing — not all founding engineers are equal. Interrogate: did the company get real traction? Tier-1 investors? Notable customers? Did the candidate actually own meaningful surface area?
- "I'm interested in this TT5 co" — interest never makes someone TT5.
- Parroting resume BS about big tech work kills your submission. Even strong candidates can shoot themselves in the foot.
- "Touched RAG/training/infra" surface-level — did they actually go DEEP? Have IMPACT? Scope (how big), Ownership (what did they do), Complexity (was it actually hard), Signal (rare or common), Business relevance (did it matter)?

TT4 GREEN FLAGS:
- Good company — doesn't have to be top tier, but still talent-dense and known to be talent-dense
- Decent communication — doesn't have to be magical, but still needed
- Good pedigree + trajectory — slope over intercept still matters, just more forgiving than TT5. Stuck talent still iffy.
- Founder/anomaly behavior — YC founders can be TT4 because technical skills may lag, startup may not have gone anywhere. Tease out via live conversation.

PLACEABILITY — best fit company tier (placeable_at). Companies named are REPRESENTATIVE — apply "or similar caliber" reasoning:
- TT5 → "TT5-hungry clients (e.g. Cursor, Decagon, Antes, Proximal, frontier AI labs, top quant, or similar bleeding-edge clients)"
- TT4 → "TT4 clients — solid VC-backed startups that aren't TT5-only (e.g. Owner, CodeRabbit, January, Brellium, Eagle, or similar caliber)"
- TT3 → "Do not submit — does not meet Candidate Labs bar"

Pool composition rule: sweet spot is towards the middle. If your pool is all borderline TT4s, you need to adjust UPWARD. Too TT5 is also bad — fewer shots on goal per candidate.

SCORING BAR (bar_score 0–10) — supporting numeric signal, anchored to talent_tier:
- 9–10 EXCEPTIONAL (TT5): Top 50 CS/STEM school + solved genuinely hard 2026-caliber problems (see role definitions below) + strong pedigree (high-growth co, top-tier VC). NOVEL AI infra builders (custom eval harnesses that catch reward hacking, long-horizon agent orchestration past the SDK layer, RL environments, inference optimization) get boosted here. Building an MCP server or basic RAG does NOT boost.
- 8 STRONG (high TT4 or TT5): Strong hard-problem evidence + either great school OR great pedigree — not necessarily both. Clear ownership, measurable outcomes.
- 7 SOLID (TT4): Good signal on hard problems but school/pedigree is moderate. Or great pedigree but problem complexity is unclear. Also: strong shippers who build on top of AI SDKs without novel infra land here, not at 8+.
- 5–6 AVERAGE (TT3 / borderline TT4): CRUD/feature work, tool-lister resume, big-co only, or no hard problem evidence. Top school alone does not exceed 6.
- 1–4 BELOW BAR (TT3 or lower): No hard problems, no measurable output, job hopping, no startup exposure, or purely tutorial/side-project experience.

HARD ENGINEERING SIGNALS BY ROLE — 2026 refresh (use these to assess problem complexity):
- Backend: distributed systems, consensus/consistency problems, high-QPS APIs, DB internals (sharding, query optimization), event-driven architecture INTERNALS (Kafka/Flink internals — not just usage), core infra other teams depend on. NOT just "built REST APIs", NOT Kafka-as-a-consumer.
- Frontend: rendering performance at scale, real-time collaborative UX (WebSockets, CRDTs, OT), design systems built from scratch, build system/bundler/runtime optimization, complex state management at scale. NOT just "added React components".
- Fullstack: full system ownership end-to-end with hard tradeoffs, real-time or highly interactive features, shipped 0→1 products with real user scale. NOT just gluing frameworks together.
- AI Engineer: NOVEL AI infra only — eval infra that actually works (verifiers, LLM-judge calibration, catching reward hacking); long-horizon agent orchestration past the SDK layer (memory, tool routing, error recovery over 100+ steps); RL environments; synthetic data pipelines; inference-side infra. NOT calling APIs, NOT basic RAG (chunk+embed+retrieve), NOT MCP servers, NOT LangChain/LlamaIndex wiring, NOT LoRA fine-tunes on OSS models alone.
- ML Engineer: model training at scale, inference optimization (custom kernels, speculative decoding, KV cache tricks, quantization at prod scale), RLHF/RLAIF, reproducing papers with novel modifications, recommendation systems at scale. NOT sklearn, NOT Jupyter notebooks, NOT LoRA on OSS models alone.
- Data Engineer: petabyte-scale pipelines, real-time streaming (Flink/Spark internals — not just usage), CDC pipelines, lakehouse architecture, data platforms serving hundreds of internal users. NOT writing ETL scripts.
- Product Designer: 0→1 design at a fast-growing startup, design systems from scratch, complex interaction systems (not just screens), shipped things that moved measurable metrics, cross-functional influence. Degree does NOT matter for this role.
- Forward Deployed Engineer: deep technical + customer-facing — custom integrations on complex enterprise APIs, automation/scripting at scale, solving hard problems on-site with customers, breadth + depth. Top 50 school and strong company pedigree both matter.
- Product Engineer: ships end-to-end with full ownership and product instincts, user-facing impact with measurable outcomes, thinks like a PM but builds like a senior engineer. 0→1 track record with real users.

COMMODITIZED IN 2025–2026 (NO LONGER hard-problem signal — do NOT boost, do NOT list as a "hard problem"):
- MCP servers — the SDK is trivial, every AI-curious dev has one
- Basic RAG (chunk + embed + retrieve + rerank)
- LangChain / LlamaIndex / off-the-shelf agent framework wiring
- LoRA fine-tunes on OSS models
- Prompt engineering as a standalone skill
- Vector DB integrations, "chatbot on our docs"
- Wrapping Claude/OpenAI APIs into an internal tool
- "Built a Cursor-like tool" / "built our own Claude Code" — depends heavily on depth; most are wrappers and should NOT auto-boost
- Sub-agent orchestration via off-the-shelf frameworks
If a candidate's AI resume is built entirely from the items above, they do not get an AI boost. Cap at 7 unless other genuinely hard problems exist. Was 8+ signal 12 months ago; now commodity.

JUNIOR SLOPE EVALUATION (0–3 YoE) — run this alongside the main rubric:
For juniors, GPA and school under-catch high-slope outliers. Parker's accepted_exemplars at tier-4/5 companies for 0–3 YoE profiles show the pattern: YC founding engineers with 0→1 traction, Waterloo new-grads with production multi-agent LLM systems, students with first-author ML papers or Neo Scholar / Pear / Z Fellows status. Score for shipping evidence, not just credentials.

Slope signals (roughly ordered by predictive power):
1. Shipping velocity with real users — 100+ non-friend users of at least one shipped thing in the last 12 months
2. Complexity trajectory — projects getting harder over time (freshman CRUD → junior distributed system → senior own-inference-server)
3. Self-directed hard choice — picked a hard problem when they didn't have to (personal infra, custom dev tools, own eval harness)
4. Debugging depth — can narrate a nasty multi-day bug hunt with specifics
5. Reads source not tutorials — cites specific commits, reads compiler output, tracks GitHub issues
6. Merged non-trivial OSS PRs in real codebases (vLLM, Modal, Next.js, LangGraph, etc.) — README typos and own repo do NOT count
7. Hackathon wins at prestige venues — SF hacker houses, YC AI Startup School, Anthropic/OpenAI/Cursor/Modal hackathons, Neo Scholar, Pear/Z Fellows. Local college hackathons ≈ noise.
8. Public technical writing showing real reasoning — deep dive into one weird thing, not "10 things I learned about LLMs"
9. Founded something used by strangers in college — bar: 100+ non-friend users
10. Beat the tools — built something before the tool existed to build it (rare, strongest single signal)

Junior escape hatches:
- School: standard bar requires top 50 CS/STEM. For juniors, signals 1+2+9 or 1+6+10 can offset a non-top-50 school. Still need a legible technical background.
- GPA: use as tiebreaker only. A 3.4 with a shipped agent framework used by 5k devs beats a 4.0 with three class projects.
- AI-native context: a junior at a 15-person AI startup shipping infra beats a junior at Google doing feature work — weight the smaller company's shipping evidence more heavily IF the work is legibly hard.

"Vibe coder" trap: A junior who shipped 20 things using Claude Code but couldn't build a hashmap = fake slope. Clients discover this at onsite. Require at least one project where they went below the abstraction (debugged at systems level, wrote lower-level code, contributed to a library rather than just consumed one). Without this evidence, cap bar_score at 6 regardless of shipping count.

Junior-specific red flags: only class projects and internships, resume padded with tutorial-completions ("built a Twitter clone", "built a chatbot on my docs"), all AI projects in the commoditized list, zero public artifacts, "AI/ML" projects that are all API calls with no evals or system design.

How to apply junior rubric: if a 0–3 YoE candidate clears the slope bar (5+ of the 10 signals, including at least one of #1/#2/#6/#10), they can score 7–8 even without top-50 school or top-tier pedigree. To score 9+, they still need the main rubric's requirements — this is about not MISSING high-slope juniors, not about lowering the top bar.

GREEN FLAGS (add to green_flags):
- Building NOVEL AI infra: custom eval harnesses, long-horizon agent orchestration past the SDK layer, RL environments, inference optimization (NOT: MCP servers, basic RAG, LangChain wiring, LoRA on OSS — those are commodity)
- Joined a company at Seed/Series A and left at Series C+ (rode the rocket)
- Unusual promotions or early leadership (IC to tech lead in <2 years)
- Side projects with real traction — real strangers using it (users, revenue, GitHub stars from strangers not friends)
- Published research, patents, or conference talks on hard problems
- Founding engineer or first/early technical hire at YC / top-VC backed company
- (Juniors) High-slope signals per junior rubric above — shipped things with real users, complexity trajectory, merged OSS PRs, prestige hackathon wins

RED FLAGS (flag ALL of these explicitly in red_flags):
- Job hopping: any role under 12 months (except internships or known layoffs), or 3+ jobs in 4 years — "Job hopping: X roles in Y years"
- No top-tier VC backing: if ALL past employers lack a16z, Sequoia, General Catalyst, Accel, Khosla, Lightspeed, YC, Benchmark, Greylock, Founders Fund, Tiger Global, Coatue, Index, Bessemer, NEA, IVP, Insight, Spark — "No top-tier VC-backed company experience"
- No hard engineering problems: only feature/CRUD work with no complexity — "No evidence of hard engineering problems"
- Resume lists tools, not outcomes: no business impact, only tech stack — "Resume lists tools, not outcomes"
- Only large-company experience (1000+ employees) — "No early-stage or startup experience"
- No top 50 CS/STEM degree (for Backend, Fullstack, AI, ML, Data, FDE roles — not required for Product Designer) — "No top 50 CS/STEM degree" (note: exceptional pedigree can offset this; for juniors, high-slope shipping evidence per junior rubric can offset)
- AI resume built entirely on commoditized items (MCP servers, basic RAG, LangChain wiring, LoRA on OSS, prompt engineering) with no novel infra — "AI experience is commoditized surface work, no novel infra"

OUTPUT FORMAT — be concise. Focus on what matters:
- hard_problems: bullet list of the 2–3 hardest things they actually built or solved
- recruiter_summary: 2–3 sentences max — why strong or why not, pedigree signal, one key flag if any
- one_liner: single sentence a recruiter says on a call — punchy, specific, no fluff
- employer_pedigree: per company — headcount at join vs leave, funding stage, notable investors, growth signal

CANDIDATE LINKS (when present — use web_search for engineering depth):
If the candidate section includes a LinkedIn URL, GitHub URL, personal site, blog, or a section labeled "EXTRA LINKS", use web_search to inspect them for signal:
- GitHub: scan for non-trivial repos, languages, recent activity, stars, contributor count. A real systems repo with thousands of lines vs. only tutorial forks is the difference between TT4 and TT5. Cite specific repos in `hard_problems` when relevant.
- Personal site / blog: look for technical writeups (architecture deep-dives, perf optimization, distributed systems posts) — that's a strong P0/P1 signal. Marketing-fluff sites are neutral.
- Papers / arXiv / Google Scholar: count first-author / top-venue papers. Note in `green_flags` if substantial.
- LinkedIn: only search if resume lacks dates/titles; don't waste a query if you already have the info.
Budget: combined with company research, max 5 web searches total. Prioritize: candidate GitHub (1 query) > most-recent employer investors (1-2 queries) > tied employer/headcount lookups.
Reflect any findings in `hard_problems`, `green_flags`, `complexity_notes`, and `talent_tier_reasoning`. Do NOT invent — if a link returns nothing useful, ignore it silently.

COMPANY RESEARCH (CRITICAL — do not default to "Unknown", but do NOT hallucinate either):
You have a `web_search` tool available. For each employer on the resume, fill in funding_stage, notable_investors, approx_funding, and headcount.

Order of operations:
1. If you are HIGHLY CONFIDENT from training (large public co, household-name startup, well-documented acquisition) — answer directly. Example: Stripe, Cloudflare, Segment-acquired-by-Twilio, etc.
2. If you are NOT certain about investors/stage/headcount — USE web_search. Query like `<company> investors crunchbase`, `<company> series funding`, `<company> headcount employees`. Prefer Crunchbase, PitchBook, TechCrunch, company press releases, LinkedIn.
3. Only after a search returns nothing useful, mark fields "Unknown".

Hard rules:
- NEVER invent investor names. If you didn't verify it (from training certainty or a search hit), do not list it. A wrong investor attribution is worse than "Unknown".
- For tier-1 backing flag (a16z/Sequoia/GC/Accel/Khosla/Lightspeed/YC/Benchmark/Greylock/Founders Fund/Index/Bessemer/NEA/IVP/Insight/Spark/Coatue/Tiger), only assert it if confirmed by training or a search result. Do NOT trigger the "no top-tier VC backing" red flag if you confirmed any employer is tier-1-backed.
- Budget at most 5 web searches total — prioritize the candidate's most recent / most prominent employers.
- For headcount: use ranges like "~50", "~200", "1000+". Mark `headcount_signal` as "High" only with a verified source (search hit or strong training confidence). Use "Moderate" for reasonable estimates from funding-round size, "Low" for guesses, "Unknown" if you truly have nothing.

Return this exact JSON:
{"candidate_name":"","verdict":"STRONG HIRE|HIRE|MAYBE|PASS","verdict_reason":"","engineering_level":"L3 (Junior)|L4 (Mid)|L5 (Senior)|L6 (Staff)|L7 (Principal/Architect)","talent_tier":"TT5|TT4|TT3","talent_tier_reasoning":"1-2 sentences on why this tier — company quality, narrative, slope vs intercept, communication signals if known","placeable_at":"","bar_score":0,"bar_label":"Exceptional|Strong|Solid|Average|Below Bar","complexity_score":0,"complexity_type":"Problem Solver|Product Builder|Infrastructure/Platform|Research/ML|Full-Stack Generalist|Specialist|Customer-Facing Technical|Design Systems|Product Strategy","complexity_notes":"","hard_problems_found":true,"hard_problems":[],"hard_problems_summary":"","best_company_stages":[],"best_company_types":[],"team_size_fit":"","roles_to_target":[],"red_flags":[],"green_flags":[],"tech_stack":[],"employer_pedigree":[{"company":"","funding_stage":"","notable_investors":[],"approx_funding":"","headcount_joined":"","headcount_left":"","headcount_signal":"High|Moderate|Low|Unknown","funding_at_join":"","pedigree_signal":"Strong|Moderate|Weak|Unknown","notes":""}],"pedigree_score":0,"pedigree_summary":"","jd_match_score":null,"jd_match_notes":null,"recruiter_summary":"","one_liner":""}'''

REFRESH_SOURCING_PROMPT = '''You are an expert technical recruiter. Generate a fresh daily sourcing plan for the given role. Return ONLY valid JSON — no markdown, no explanation.

Return this exact JSON:
{
  "angle": "1-2 sentence fresh angle or insight for sourcing this role today — something specific and actionable",
  "booleans": [
    "full LinkedIn Recruiter boolean string #1",
    "full Google X-Ray boolean string #2"
  ],
  "targets": [
    {"company": "CompanyName (Stage)", "reason": "Why this is a great poaching target right now — be specific"},
    {"company": "CompanyName (Stage)", "reason": "..."},
    {"company": "CompanyName (Stage)", "reason": "..."},
    {"company": "CompanyName (Stage)", "reason": "..."},
    {"company": "CompanyName (Stage)", "reason": "..."}
  ],
  "tactics": [
    "Specific tactic or channel to try today — niche and actionable",
    "Another tactic",
    "Another tactic"
  ]
}'''

PITCH_SYSTEM_PROMPT = '''You are an expert technical recruiter at SingleSprout building phone-ready pitches. Given a candidate profile and available companies, match and generate 3-5 top pitches a recruiter would say out loud on a live call.

Rules:
- Lead with the best match for THIS specific candidate — not alphabetical, not highest stage
- The "why_fit" sentence is everything — tie it to something specific from their background
- Keep each pitch tight: 2-4 sentences max, say-able on a call
- Use natural recruiter speech: "So the first one I'm really excited about for you is...", "Next one is...", "Then there's..."
- Skip companies where location, visa, or tech stack clearly don't match
- Flag anything that could blow up on a call (unusual culture, visa unclear, stage mismatch)

Return ONLY valid JSON:
{
  "pitches": [
    {
      "company": "Name",
      "funding_stage": "Series X",
      "opener": "So the first one I'm really excited about for you is [Company]...",
      "why_fit": "One sentence tying this to the candidate specifically",
      "details": "Team size, what they're hiring for, location/office policy",
      "flag": "Warning for recruiter or null"
    }
  ],
  "flags_block": "Overall notes or null",
  "match_count": 3
}'''

SUGGESTIONS_SYSTEM_PROMPT = '''You are a senior technical recruiter at Candidate Labs ranking company suggestions for a candidate. Use the company data provided — which includes Parker CRM details and, where available, real insight canvas data pulled from client Slack channels — to return 8-12 ranked suggestions.

MATCH AGAINST REVEALED PREFERENCE, NOT THE STATED HEADLINE (read first):
The strongest matching signal — when present in the company data — is the client's HIRING PROFILE: empirical, revealed-preference data showing which candidates the client actually accepted. Specifically:
  - `accepted_exemplars` — real accepted candidates (headline + career ladder + YOE), each flagged by how far it progressed (`stage: submitted` / `onsite` / `offer` / `accepted`). Weight exemplars flagged `onsite` / `offer` / `accepted` most heavily — those are the people who actually advanced.
  - `progressed_cohort` / `overall` fingerprint — aggregate archetypes, YOE band, companies, schools. `progressed_cohort: null` means too few advanced to aggregate — NOT that nobody fits; the stage-flagged exemplars still carry the signal. Treat single-digit counts as directional.
  - `stage_funnel` — conversion ratios. A healthy `reached_offer / accepted_for_submission` ratio means the client genuinely advances people; a large `accepted_for_submission` with near-zero `reached_onsite` means they accept for submission but rarely advance — calibrate and lean on `overall` fingerprint + rejection traits.
Match the candidate against these *actual* accepted backgrounds — not against archetype tags alone (they're broad). The accepted_skillsets / accepted_backgrounds lists in `insiders_note` are the fallback when richer hiring profile fields aren't present. Don't keyword-match: "infrastructure" at Google ≠ "infrastructure" at a 5-person startup — use judgment about what experience actually transfers.

RANKING RULES (apply in order):
1. LOCATION — Hard filter first:
   - If candidate specifies a city (NYC, SF, etc.) and is NOT open to relocation or remote: exclude companies requiring in-office in a different city
   - Remote or remote-friendly companies always pass regardless of candidate location
   - If no location constraint is specified: include all, but flag mismatches with ⚠️

2. TALENT TIER — Match the candidate's talent_tier to the client's tier appetite. This is the #1 placement signal, but NOT the only one — scope match + motivators can justify a stretch (see below):
   - TT5 candidate → lead with TT5-hungry clients (e.g. Cursor, Decagon, Antes AI, Proximal, Causal Labs, frontier AI labs, top quant). TT5s can also submit to TT4 clients, but lead with TT5-hungry first.
   - High TT4 / borderline TT5 (talent_tier=TT4 AND bar_score=8) → Lead with TT4-friendly clients first (safe bets), but append 2-3 TT5 stretch suggestions. Each stretch MUST have watch_out: "Stretch: high TT4 (bar 8) — confirm with recruiter before submitting to TT5 client".
   - TT4 candidate (bar_score ≤ 7) → LEAD with TT4-friendly clients (e.g. Owner, CodeRabbit, January, Brellium, Eagle, Agave, Govwell, Instrumentl). BUT — still surface 2-3 TT5 stretch candidates IF there's a strong scope + motivator match (see TT4→TT5 STRETCH RULE below). Don't blindly exclude all TT5s. If a TT5 client wants "true TT5 / Cursor caliber / frontier-only" with no scope flexibility, exclude.
   - TT3 / unknown / minimal-info candidate → STILL return 5-10 best-fit matches based on role + location + stack. Set watch_out on each to "Below Candidate Labs typical bar — confirm fit before submitting." Add a flags_block note acknowledging the tier gap. Never return zero suggestions just because tier is low or missing.
   - Set watch_out to flag any tier-stretch (e.g. "Client wants true TT5 — candidate is high TT4, may be a stretch").

TT4→TT5 STRETCH RULE (NEW — read carefully):
A TT4 candidate (bar 6-7) can be pitched to a TT5 client when BOTH apply:
  (a) ROLE SCOPE match: the TT5 client's open role is a scope they can credibly grow into — e.g. the client needs a "first product engineer" but the candidate has shipped 0→1 product before; or the client needs someone to own a domain the candidate has actually owned. Generic "senior eng" reqs at frontier-only clients don't count.
  (b) MOTIVATOR match: the recruiter notes / motivators show this is what the candidate actually wants — e.g. "wants to lead a domain", "burned out on big-co, wants 0→1", "wants AI exposure", "wants founding-eng energy" — AND the client offers exactly that.
When both apply, include the TT5 client as a stretch with watch_out: "TT5 stretch — candidate is TT4 (bar X) but role scope + motivators ('<the specific motivator>') align. Confirm with client before submitting." Cap stretches at 2-3 per candidate. Skip if the TT5 client's insight data explicitly rejects this profile.

USE MOTIVATORS EVERYWHERE:
If RECRUITER NOTES & MOTIVATORS are included in the candidate section, weight them heavily in why_match. A candidate saying "wants B2C product surface" should rank consumer-facing companies above infra, even if both are technically fits. Quote the motivator in why_match when it's the deciding signal.

3. INSIGHT DATA — When a company has insight canvas data, use it as a strong signal:
   - Match "Accepted Skillsets" and "Accepted Backgrounds" to candidate → boosts rank
   - REJECTION TRAITS ARE THE STRONGEST DISQUALIFIER. If candidate matches a "Rejected Trait", treat it as a HARD NO regardless of how good the skillset/tier match is — a company that rejects "5+ YOE" won't accept your 7-YOE candidate. Common patterns: too senior/too junior, big-tech without startup exposure (or vice versa), wrong function (frontend when they want backend), comp above range, visa/location mismatch. Only override with explicit recruiter justification.
   - Note any hard requirements in "Other Signals" (comp ceiling, education, timing)
   - SIGNAL RECENCY: if `signal_age_days` > 30, treat as a caveat — note it in watch_out (e.g. "Insight signal is 45 days old — re-verify"). Hiring profile data covers a rolling 90-day window.

4. ROLE + DOMAIN FIT — Does the company hire this role? Does their domain match the candidate background?

5. STAGE — Match candidate stage preference if provided

Companies with strong insight alignment + tier alignment should rank ABOVE companies with only Parker data and no insight. Be specific in why_match — tie it to something from their actual background AND the tier fit.

Return ONLY valid JSON with no markdown fences, no explanation, nothing else:
{
  "suggestions": [
    {
      "company": "Name",
      "funding_stage": "Series X",
      "fit_score": 8,
      "location_status": "Match",
      "location_detail": "NYC (hybrid) — candidate is NYC-based",
      "why_match": "1 sentence tying this specific candidate to this specific company",
      "insight_summary": "What the client actually wants based on insight data: key accepted signals, hard requirements. Omit if no insight data.",
      "watch_out": "Specific rejection risk from Rejected Traits, comp mismatch, or visa issue. null if none."
    }
  ],
  "total_count": 10,
  "flags_block": "Any overall note (e.g. location pool is thin, stage filters applied) or null"
}'''

# ─── Fallback Companies (from sourcing playbook) ───────────────────────────────

FALLBACK_COMPANIES = [
    {"name": "Neon", "categories": ["Backend", "Infrastructure"], "funding_stage": "Series B", "overview": "Postgres-compatible serverless database. a16z backed.", "locations": ["Remote", "NYC", "SF"], "office_policy": "Remote-friendly", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Senior backend engineers with distributed systems or DB experience", "insiders_note": "Deep systems engineers who want to own real infra problems — tiny team, huge scope."},
    {"name": "Linear", "categories": ["Frontend", "Product Designer", "Product Manager", "Fullstack"], "funding_stage": "Series B", "overview": "Issue tracking with legendary design culture. Sequoia backed.", "locations": ["SF", "Remote"], "office_policy": "Remote-friendly", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Engineers who care deeply about craft and product quality", "insiders_note": "The gold standard for product culture. If they care about craft, this lands."},
    {"name": "Vercel", "categories": ["Frontend", "Infrastructure", "Fullstack"], "funding_stage": "Series D", "overview": "Frontend cloud platform, home of Next.js. GV/Accel backed.", "locations": ["SF", "Remote"], "office_policy": "Remote-friendly", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Frontend and fullstack engineers at the edge of the ecosystem", "insiders_note": ""},
    {"name": "Temporal", "categories": ["Backend", "Forward Deployed Engineer"], "funding_stage": "Series B", "overview": "Workflow orchestration platform. Sequoia backed.", "locations": ["SF", "NYC", "Remote"], "office_policy": "Hybrid", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Senior backend engineers who understand durable execution and complex systems", "insiders_note": ""},
    {"name": "Raycast", "categories": ["Frontend", "Product Designer"], "funding_stage": "Series A", "overview": "Craft-obsessed productivity tool for Mac. Accel backed.", "locations": ["Remote"], "office_policy": "Fully remote", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Frontend engineers and product designers obsessed with UX quality", "insiders_note": "Pixel-perfect, interaction-heavy. Great for designers who want real ownership."},
    {"name": "Retool", "categories": ["Fullstack", "Forward Deployed Engineer", "Product Manager"], "funding_stage": "Series C", "overview": "Internal tools platform. Sequoia/a16z backed.", "locations": ["SF"], "office_policy": "In-office (5x/week)", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Full-stack engineers who own entire product surfaces, FDEs with customer + build chops", "insiders_note": "Heads up — 5x/week in-office in SF. Confirm before pitching remote candidates."},
    {"name": "Cursor", "categories": ["AI Engineer", "Backend", "Fullstack"], "funding_stage": "Series B", "overview": "AI code editor. a16z/Thrive backed.", "locations": ["SF"], "office_policy": "In-office preferred", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "AI engineers with LLM/agent experience, strong backend or fullstack", "insiders_note": ""},
    {"name": "Perplexity", "categories": ["AI Engineer", "Backend", "ML Engineer"], "funding_stage": "Series B", "overview": "AI search engine. Nvidia/NEA backed.", "locations": ["SF"], "office_policy": "In-office", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "AI/ML engineers with RAG, retrieval, or search at scale experience", "insiders_note": ""},
    {"name": "Fly.io", "categories": ["Infrastructure", "Backend"], "funding_stage": "Series B", "overview": "Edge compute platform. a16z backed.", "locations": ["Remote"], "office_policy": "Fully remote", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Infrastructure engineers who understand distributed deployment and multi-region", "insiders_note": ""},
    {"name": "Rippling", "categories": ["Backend", "Fullstack", "Product Manager"], "funding_stage": "Series F", "overview": "Compound startup for workforce management. Sequoia/Founders Fund backed.", "locations": ["SF", "NYC"], "office_policy": "Hybrid", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Senior engineers and PMs with complex multi-product experience", "insiders_note": "High-intensity culture — worth flagging expectations."},
    {"name": "Cohere", "categories": ["ML Engineer", "AI Engineer", "Backend"], "funding_stage": "Series C", "overview": "Enterprise LLM platform. General Catalyst/Nvidia backed.", "locations": ["NYC", "SF", "Toronto", "Remote"], "office_policy": "Hybrid", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "ML engineers with training, inference, or RLHF experience", "insiders_note": ""},
    {"name": "Supabase", "categories": ["Fullstack", "Frontend", "Backend"], "funding_stage": "Series C", "overview": "Open source Firebase alternative. Lightspeed backed.", "locations": ["Remote"], "office_policy": "Fully remote", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Full-stack engineers who ship OSS and own the whole stack", "insiders_note": ""},
    {"name": "dbt Labs", "categories": ["Data Engineer"], "funding_stage": "Series D", "overview": "Modern data transformation. Sequoia/Andreessen backed.", "locations": ["Remote"], "office_policy": "Remote-first", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Data engineers with dbt, Airflow, and modern data stack experience", "insiders_note": ""},
    {"name": "Framer", "categories": ["Frontend", "Product Designer"], "funding_stage": "Series B", "overview": "Design-to-code tool. Accel backed.", "locations": ["Amsterdam", "Remote"], "office_policy": "Remote-friendly", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Frontend engineers and designers who understand design deeply", "insiders_note": ""},
    {"name": "Notion", "categories": ["Fullstack", "Frontend", "Product Manager", "Product Designer"], "funding_stage": "Series C", "overview": "All-in-one workspace. Sequoia/Index backed.", "locations": ["SF", "NYC", "Remote"], "office_policy": "Hybrid", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Engineers with PLG experience, strong fullstack or product chops", "insiders_note": ""},
    {"name": "Anduril", "categories": ["Forward Deployed Engineer", "Backend", "Infrastructure"], "funding_stage": "Series F", "overview": "Defense tech, embedded engineers in the field. Founders Fund/a16z backed.", "locations": ["Newport Beach", "SF", "Austin"], "office_policy": "In-office", "visa_support": "US Citizens only", "talent_tier": "Tier 1", "who_to_pitch": "FDEs or engineers comfortable with defense/national security work", "insiders_note": "US citizens only — hard filter. In-office required."},
    {"name": "Scale AI", "categories": ["Forward Deployed Engineer", "ML Engineer", "Backend"], "funding_stage": "Series F", "overview": "AI data infrastructure. Accel/Tiger Global backed.", "locations": ["SF"], "office_policy": "In-office", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "FDEs, ML engineers, backend engineers with customer-facing technical work", "insiders_note": ""},
    {"name": "Brex", "categories": ["Backend", "Product Manager", "Fullstack"], "funding_stage": "Series D", "overview": "Fintech infrastructure. Greenoaks/Ribbit backed.", "locations": ["SF", "NYC", "Remote"], "office_policy": "Hybrid", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Backend engineers and PMs with fintech or compliance depth", "insiders_note": ""},
    {"name": "Plaid", "categories": ["Backend", "Fullstack"], "funding_stage": "Series D", "overview": "Financial data network. Andreessen/Goldman backed.", "locations": ["SF", "NYC", "Remote"], "office_policy": "Hybrid", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Backend engineers with API infrastructure or fintech experience", "insiders_note": ""},
    {"name": "Stripe", "categories": ["Backend", "Fullstack", "Forward Deployed Engineer"], "funding_stage": "Public (pre-IPO)", "overview": "Payments infrastructure. Sequoia/General Catalyst backed.", "locations": ["SF", "NYC", "Remote"], "office_policy": "Hybrid", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Backend engineers who want world-class infra culture and scale", "insiders_note": ""},
    {"name": "Figma", "categories": ["Frontend", "Product Designer", "Backend"], "funding_stage": "Public (post-Adobe)", "overview": "Design tool turned platform.", "locations": ["SF", "NYC", "Remote"], "office_policy": "Hybrid", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Engineers and designers wanting to work on design tooling at scale", "insiders_note": ""},
    {"name": "Datadog", "categories": ["Infrastructure", "Backend", "Data Engineer"], "funding_stage": "Public", "overview": "Observability and monitoring platform.", "locations": ["NYC", "SF", "Remote"], "office_policy": "Hybrid", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Infra and backend engineers with observability or monitoring stack experience", "insiders_note": ""},
    {"name": "PlanetScale", "categories": ["Backend", "Infrastructure"], "funding_stage": "Series C", "overview": "MySQL-compatible serverless database. a16z backed.", "locations": ["Remote"], "office_policy": "Fully remote", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Database engineers, backend engineers who want to own deep DB infra", "insiders_note": ""},
    {"name": "Clerk", "categories": ["Frontend", "Backend", "Fullstack"], "funding_stage": "Series B", "overview": "Auth infrastructure with premium DX. Madrona/YC backed.", "locations": ["Remote"], "office_policy": "Remote-first", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Frontend-heavy engineers with strong craft bar", "insiders_note": ""},
    {"name": "Glean", "categories": ["Forward Deployed Engineer", "AI Engineer", "Backend"], "funding_stage": "Series D", "overview": "Enterprise AI search. Sequoia/Lightspeed backed.", "locations": ["Palo Alto", "NYC"], "office_policy": "In-office", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "FDEs who help enterprise customers deploy and extract value from AI", "insiders_note": ""},
    {"name": "Modal", "categories": ["ML Engineer", "Infrastructure", "Backend"], "funding_stage": "Series B", "overview": "Cloud for ML workloads. Redpoint backed.", "locations": ["Remote", "NYC"], "office_policy": "Remote-friendly", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "ML engineers who understand GPU infra and ML pipelines end to end", "insiders_note": ""},
    {"name": "Replicate", "categories": ["ML Engineer", "Backend"], "funding_stage": "Series B", "overview": "Model hosting platform. a16z backed.", "locations": ["Remote"], "office_policy": "Fully remote", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "ML engineers who ship models to production and care about DX", "insiders_note": ""},
    {"name": "Mistral AI", "categories": ["ML Engineer", "AI Engineer"], "funding_stage": "Series B", "overview": "Open-weight frontier models. Lightspeed/a16z backed.", "locations": ["Paris", "Remote"], "office_policy": "Hybrid", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Research-grade ML engineers interested in frontier model development", "insiders_note": "Paris-based HQ — worth flagging location expectations."},
    {"name": "Hightouch", "categories": ["Data Engineer", "Backend"], "funding_stage": "Series B", "overview": "Reverse ETL and data activation. a16z/Bain backed.", "locations": ["SF", "Remote"], "office_policy": "Remote-friendly", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Data engineers who think about activation and moving data between systems", "insiders_note": ""},
    {"name": "Arc Browser", "categories": ["Product Designer", "Frontend"], "funding_stage": "Series B", "overview": "Reinvented the browser — bold product design. General Catalyst backed.", "locations": ["NYC"], "office_policy": "In-office", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Opinionated product designers and frontend engineers who want to reshape UX", "insiders_note": ""},
    {"name": "D.E. Shaw Research", "categories": ["AI Engineer", "ML Engineer", "Backend"], "funding_stage": "Other", "overview": "AI + molecular simulation for drug discovery. Privately held, founded by David Shaw. ~120 people in NYC with mature ML team and growing agentic AI group.", "locations": ["NYC"], "office_policy": "Hybrid (Tues–Thurs)", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "Strong research engineers (pretraining, postraining, evals) who want startup-caliber ownership with serious resources. Strong LLM agent harness engineers.", "insiders_note": "LEAD with: this is NOT the hedge fund. It's a small, well-resourced AI research company. $300–800K cash comp. Agentic AI team is only 2 FT + interim lead — major growth priority. NYC relocation is the main friction; counter with high cash, hybrid flexibility, and exceptional compute (rivals frontier labs)."},
    {"name": "Citizen Health", "categories": ["AI Engineer", "Backend", "Fullstack"], "funding_stage": "Series A", "overview": "AI patient advocate for rare disease navigation. 8VC backed. Repeat founder Farid Vij ($550M exit) + ex-Uber/Amazon CTO Daniel Wang leading ~16-person eng team.", "locations": ["SF"], "office_policy": "Hybrid (Tues–Thurs)", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "AI-native product engineers obsessed with 0→1 systems, agentic workflows, and real-world healthcare impact. Former founders/CTOs and founding engineers with 0→1 experience.", "insiders_note": "Very active client — Farid personally screens all candidates. Strong acceptance rate (15/18 last 90 days). Rejected traits: short tenures, traditional ML without LLM depth, <5 years experience. H1B transfers not a barrier. Candidates competing with Katalyze."},
    {"name": "Catalyst", "categories": ["AI Engineer", "Backend", "Fullstack"], "funding_stage": "Seed", "overview": "Intent-based trading platform via natural language. $20M seed at $300M+ valuation, Sequoia + Jump Trading backed. 4-person team in Palo Alto.", "locations": ["SF", "SF Bay Peninsula"], "office_policy": "In-person preferred", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "True TT5 risk-seeking senior/staff builders from talent-dense cultures (Ramp, Palantir, Cursor-type). Min 5 YOE. Excited to join before the product is fully figured out.", "insiders_note": "Very early — pitch as 'early Cursor moment for finance.' Jump Trading is not just an investor but a potential institutional user. Be direct about intensity: team is basically online whenever not sleeping. Do not pitch as a proven product motion."},
    {"name": "Nexon", "categories": ["Backend", "AI Engineer", "ML Engineer"], "funding_stage": "Seed", "overview": "Vision-based computer-use agents automating healthcare operations (EHRs, insurance portals, claim denials). 8VC backed. ~6 months old, scaling revenue rapidly.", "locations": ["SF"], "office_policy": "In-office (5x/week)", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "TT4–TT5 SF-based high-slope backend/systems engineers and applied ML/research engineers excited by rigorous AI agent infrastructure work in healthcare.", "insiders_note": "Founders: Shashwat Kishore (sold Dorsal Health to Commure, Harvard CS) + Meera (Apple healthcare data, Stanford). Slope over intercept — cast wide for raw intellect. Can't use Anthropic/Gemini off-shelf (on-prem/PHI constraints); building custom small vision models. Up to ~$275K + meaningful equity."},
    {"name": "Titan", "categories": ["Fullstack", "AI Engineer", "Backend"], "funding_stage": "Series A", "overview": "AI-native private wealth management RIA. a16z + General Catalyst backed. ~$400M AUM, NPS jumped from 15→75. NYC, in-office 5x/week.", "locations": ["NYC"], "office_policy": "In-office (5x/week)", "visa_support": "Yes", "talent_tier": "Tier 1", "who_to_pitch": "TT5 full-stack engineers who want intense ownership and high-talent-density culture building a consumer AI product with massive distribution potential.", "insiders_note": "Founder Joe Percoco (ex-Goldman). Four-floor townhouse in Greenwich Village. Best for entrepreneurial builders with CS fundamentals, 3+ YOE, bias toward high-output in-person teams. Pitch as 'Goldman-level wealth management in your pocket' for OpenAI/Anthropic/SpaceX employees with new wealth."},
]

# ─── Helpers ────────────────────────────────────────────────────────────────────

def get_api_key():
    key = os.environ.get('ANTHROPIC_API_KEY', '').strip()
    if not key and CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
            key = config.get('api_key', '').strip()
        except Exception:
            pass
    return key

def save_api_key(key):
    config = {}
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    config['api_key'] = key
    CONFIG_FILE.write_text(json.dumps(config, indent=2))

# ─── Ashby config (lives in same ~/.recruiter-ui-config.json) ──────────────────

def _load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            return {}
    return {}

def _save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

def get_ashby_templates():
    """Saved GraphQL query templates {operationName: query_string}, captured from
    a user-pasted curl on first run. Reused across sync runs so the user only
    has to paste a fresh session-bearing curl each time the cookie/CSRF rotates."""
    return _load_config().get('ashby_templates') or {}

def save_ashby_templates(templates):
    cfg = _load_config()
    cfg['ashby_templates'] = templates
    _save_config(cfg)

# Backwards-compat shims so /api/config doesn't crash if older callers ask.
def get_ashby_key():
    """Legacy. We no longer use an API key — we use a pasted session cookie + CSRF
    per sync run. Returns whatever might be in config for display only."""
    return _load_config().get('ashby_api_key', '').strip()

def get_ashby_user_id():
    return _load_config().get('ashby_user_id', '').strip()

# ─── Ashby cURL parsing ────────────────────────────────────────────────────────
# Ashby's frontend talks to https://app.ashbyhq.com/api/graphql with:
#   - cookie:  ashby_session_token=...  (HttpOnly, signed; rotates daily-ish)
#   - header:  x-csrf-token: ...        (rotates per request burst)
#   - body:    { operationName, variables, query }
# Since the user isn't an admin and can't get an API key, we accept a "Copy as
# cURL" paste from their browser DevTools and extract those pieces. The pasted
# curl ALSO contains a real GraphQL query body, so we save those query strings
# as templates the first time we see each operation.

def parse_ashby_curl(curl_text):
    """Extract {cookie, csrf, operationName, query, variables, raw_body} from a
    pasted 'Copy as cURL' string. Tolerates both bash (-H 'k: v') and cmd
    (-H "k: v") quoting, and tolerates --data-raw vs --data vs -d."""
    if not curl_text or not isinstance(curl_text, str):
        return None, 'empty curl'
    text = curl_text.strip()
    # Collapse line continuations (' \\\n  ' or '^\n  ')
    text = re.sub(r'\\\s*\n\s*', ' ', text)
    text = re.sub(r'\^\s*\n\s*', ' ', text)

    # Extract all -H / --header pairs. Header value may be single- or double-quoted.
    headers = {}
    for m in re.finditer(r"-H\s+'([^']+)'", text):
        kv = m.group(1)
        if ':' in kv:
            k, v = kv.split(':', 1)
            headers[k.strip().lower()] = v.strip()
    for m in re.finditer(r'-H\s+"((?:[^"\\]|\\.)+)"', text):
        kv = m.group(1).encode('utf-8').decode('unicode_escape')
        if ':' in kv:
            k, v = kv.split(':', 1)
            headers[k.strip().lower()] = v.strip()

    # Extract -b / --cookie if present (Chrome sometimes uses -b instead of -H 'cookie:')
    cookie_from_flag = None
    mb = re.search(r"-b\s+'([^']+)'", text) or re.search(r'-b\s+"((?:[^"\\]|\\.)+)"', text)
    if mb:
        cookie_from_flag = mb.group(1)
        if mb.re.pattern.startswith('-b\\s+"'):
            cookie_from_flag = cookie_from_flag.encode('utf-8').decode('unicode_escape')

    cookie = headers.get('cookie') or cookie_from_flag or ''
    csrf = headers.get('x-csrf-token') or ''

    # Extract --data-raw / --data / -d body.
    body = None
    for flag in (r"--data-raw\s+\$?'((?:[^'\\]|\\.)*)'",
                 r'--data-raw\s+"((?:[^"\\]|\\.)*)"',
                 r"--data\s+'((?:[^'\\]|\\.)*)'",
                 r'--data\s+"((?:[^"\\]|\\.)*)"',
                 r"-d\s+'((?:[^'\\]|\\.)*)'",
                 r'-d\s+"((?:[^"\\]|\\.)*)"'):
        m = re.search(flag, text)
        if m:
            body = m.group(1)
            # Bash $'...' uses C-string escapes; \' inside single quotes stays as \'.
            body = body.replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')
            try:
                body = body.encode('utf-8').decode('unicode_escape')
            except Exception:
                pass
            break

    op_name = None
    query = None
    variables = None
    if body:
        try:
            j = json.loads(body)
            op_name = j.get('operationName')
            query = j.get('query')
            variables = j.get('variables')
        except Exception:
            pass

    if not cookie:
        return None, 'no cookie found in curl (paste needs Cookie header or -b flag)'
    # CSRF is technically optional for some operations but Ashby requires it for writes
    # and most reads — surface a clear hint if missing.
    return {
        'cookie': cookie,
        'csrf': csrf,
        'operationName': op_name,
        'query': query,
        'variables': variables,
        'raw_body': body,
    }, None


def call_ashby_graphql(op_name, variables, query, cookie, csrf, timeout=30):
    """POST a GraphQL request to app.ashbyhq.com. Returns (json_data, error_string)."""
    url = f'https://app.ashbyhq.com/api/graphql?op={urllib.parse.quote(op_name)}'
    body_obj = {'operationName': op_name, 'variables': variables or {}, 'query': query}
    body = json.dumps(body_obj).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept', '*/*')
    req.add_header('Cookie', cookie)
    if csrf:
        req.add_header('X-Csrf-Token', csrf)
    # Mimic the Apollo client headers Ashby's frontend sends, otherwise the API
    # sometimes rejects with "operation not allowed".
    req.add_header('Apollographql-Client-Name', 'frontend_user')
    req.add_header('Apollographql-Client-Version', '201.0.0')
    req.add_header('X-Ashby-App', 'Recruiting')
    req.add_header('Origin', 'https://app.ashbyhq.com')
    req.add_header('Referer', 'https://app.ashbyhq.com/')
    req.add_header('User-Agent', 'Mozilla/5.0 (recruiter-ui local sync)')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode('utf-8', errors='replace')
        data = json.loads(raw)
        if 'errors' in data and data['errors']:
            msgs = '; '.join((e.get('message') or '') for e in data['errors'])
            return data, f'GraphQL: {msgs[:300]}'
        return data, None
    except urllib.error.HTTPError as e:
        msg = e.read().decode('utf-8', errors='replace') if hasattr(e, 'read') else str(e)
        if e.code in (401, 403):
            return None, f'Ashby auth failed ({e.code}). Cookie/CSRF likely expired — paste a fresh curl.'
        return None, f'HTTP {e.code}: {msg[:200]}'
    except Exception as e:
        return None, f'{type(e).__name__}: {e}'

def call_claude(system_prompt, user_message, api_key, model='claude-sonnet-4-6', tools=None, timeout=120):
    url = 'https://api.anthropic.com/v1/messages'
    body = {
        'model': model,
        'max_tokens': 8192,
        'system': system_prompt,
        'messages': [{'role': 'user', 'content': user_message}]
    }
    if tools:
        body['tools'] = tools
    payload = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('x-api-key', api_key)
    req.add_header('anthropic-version', '2023-06-01')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read())
            # Concatenate all text blocks (web_search returns interleaved search results + text)
            texts = [b.get('text', '') for b in result.get('content', []) if b.get('type') == 'text']
            return ('\n'.join(t for t in texts if t).strip() or ''), None
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8')
        return None, f'API error {e.code}: {err}'
    except Exception as e:
        return None, str(e)

def parse_json_response(text):
    """Robustly extract a JSON object from a model response that may include
    prose preamble, markdown ```json fences, or interleaved tool-use text blocks
    (web_search produces these). Walks braces with string-awareness so the
    matcher doesn't choke on stray `{` / `}` inside string values."""
    import re
    clean = (text or '').strip()
    # 1) Prefer JSON inside an explicit ```json ... ``` fence (most reliable).
    fence = re.search(r'```(?:json|JSON)?\s*\n([\s\S]*?)\n```', clean)
    if fence:
        inner = fence.group(1).strip()
        obj, err = _extract_first_json_object(inner)
        if obj is not None:
            return obj, None
    # 2) Strip stray code fences and try the whole string.
    stripped = re.sub(r'^```[a-zA-Z]*\n?', '', clean, flags=re.MULTILINE)
    stripped = re.sub(r'\n?```\s*$', '', stripped, flags=re.MULTILINE).strip()
    try:
        return json.loads(stripped), None
    except Exception:
        pass
    # 3) Walk braces to extract the first balanced JSON object anywhere in the text.
    obj, err = _extract_first_json_object(stripped)
    if obj is not None:
        return obj, None
    return None, err or 'No JSON object found in response'


def _extract_first_json_object(s):
    """Find the first balanced {...} object and return (parsed, err). String-aware
    so braces inside JSON string values don't break depth tracking."""
    start = s.find('{')
    if start == -1:
        return None, 'no opening brace'
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(s[start:i+1]), None
                    except Exception as e:
                        return None, f'json.loads: {e}'
    return None, 'unbalanced braces'

def get_insight_data():
    if SLACK_INSIGHT_CACHE.exists():
        try:
            return json.loads(SLACK_INSIGHT_CACHE.read_text())
        except Exception:
            pass
    return {'companies': {}, 'last_updated': None}

def call_parker_mcp_tool(tool_name, arguments):
    import queue
    config_path = pathlib.Path.home() / 'Library/Application Support/Claude/claude_desktop_config.json'
    try:
        config = json.loads(config_path.read_text())
        args_list = config['mcpServers']['parker']['args']
        mcp_url = next(a for a in args_list if a.startswith('https://'))
        base_url = mcp_url.split('/mcp/')[0]
        hdr_idx = args_list.index('--header')
        token = args_list[hdr_idx + 1].split('Bearer ')[1].strip()
    except Exception as e:
        return None, f'Parker config error: {e}'

    result_queue = queue.Queue()

    def read_sse():
        try:
            req = urllib.request.Request(
                f'{base_url}/mcp/sse',
                headers={'Authorization': f'Bearer {token}'}
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                buf = ''
                current_event = None
                posted = False
                while True:
                    chunk = resp.read(512).decode('utf-8', errors='replace')
                    if not chunk:
                        break
                    buf += chunk
                    while '\n' in buf:
                        line, buf = buf.split('\n', 1)
                        line = line.rstrip('\r')
                        if line.startswith('event:'):
                            current_event = line[6:].strip()
                        elif line.startswith('data:'):
                            data_str = line[5:].strip()
                            if current_event == 'endpoint' and not posted:
                                posted = True
                                session_url = base_url + data_str
                                def do_post(url=session_url):
                                    payload = json.dumps({
                                        'jsonrpc': '2.0', 'id': 1,
                                        'method': 'tools/call',
                                        'params': {'name': tool_name, 'arguments': arguments}
                                    }).encode()
                                    post_req = urllib.request.Request(
                                        url, data=payload,
                                        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
                                        method='POST'
                                    )
                                    try:
                                        urllib.request.urlopen(post_req, timeout=30)
                                    except Exception:
                                        pass
                                threading.Thread(target=do_post, daemon=True).start()
                            elif current_event == 'message' and data_str:
                                try:
                                    msg = json.loads(data_str)
                                    if isinstance(msg, dict) and msg.get('id') == 1:
                                        content = msg.get('result', {}).get('content', [])
                                        text = ''.join(c.get('text', '') for c in content if c.get('type') == 'text')
                                        result_queue.put(('ok', json.loads(text)))
                                        return
                                except Exception as e:
                                    result_queue.put(('err', f'Parse error: {e}'))
                                    return
        except Exception as e:
            result_queue.put(('err', str(e)))

    threading.Thread(target=read_sse, daemon=True).start()
    try:
        status, value = result_queue.get(timeout=60)
        return (value, None) if status == 'ok' else (None, value)
    except queue.Empty:
        return None, 'Timeout waiting for Parker MCP response'


def _transform_parker_companies(raw_companies):
    """Transform Parker MCP company objects to the UI company format."""
    role_map = [
        ('backend', 'Backend'), ('frontend', 'Frontend'),
        ('full stack', 'Fullstack'), ('fullstack', 'Fullstack'),
        ('ml engineer', 'ML Engineer'), ('machine learning', 'ML Engineer'),
        ('ai engineer', 'AI Engineer'),
        ('data engineer', 'Data Engineer'), ('data ', 'Data Engineer'),
        ('infra', 'Infrastructure'), ('platform', 'Infrastructure'),
        ('product engineer', 'Product Engineer'), ('product ', 'Product Engineer'),
    ]
    companies = []
    for co in raw_companies:
        tier_raw = str(co.get('talent_tier', ''))
        tier = 'TT5' if tier_raw == '5' else ('TT4' if tier_raw == '4' else tier_raw)
        searches = co.get('active_searches', [])
        cats = []
        for s in searches:
            sl = s.lower()
            for kw, label in role_map:
                if kw in sl:
                    cats.append(label)
                    break
            else:
                cats.append('Engineering')
        companies.append({
            'company_id': co.get('company_id'),
            'name': co.get('name', ''),
            'funding_stage': co.get('funding_stage', ''),
            'talent_tier': tier,
            'locations': co.get('geos', []),
            'categories': list(dict.fromkeys(cats)) or ['Engineering'],
            'active_searches': searches,
            'overview': '',
            'office_policy': '',
            'visa_support': '',
            'who_to_pitch': '',
            'insiders_note': co.get('hiring_signals_headline', ''),
            'signal_date': co.get('signal_date'),
            'signal_age_days': co.get('signal_age_days'),
        })
    return companies


def get_parker_data():
    if PARKER_CACHE.exists():
        try:
            data = json.loads(PARKER_CACHE.read_text())
            if data.get('companies'):
                return data
        except Exception:
            pass
    return {
        'last_refreshed': None,
        'companies': FALLBACK_COMPANIES,
        '_source': 'builtin'
    }

# ─── HTTP Handler ────────────────────────────────────────────────────────────────

class RecruiterHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress server logs

    def send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, content):
        body = content.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        # Single-user dev tool. Always serve fresh so code edits propagate without
        # requiring Cmd+Shift+R. Prevents the "I refreshed but bug persists" footgun.
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        path = self.path.split('?')[0]
        if path in ('/', '/index.html'):
            html_path = SCRIPT_DIR / 'index.html'
            if html_path.exists():
                self.send_html(html_path.read_text(encoding='utf-8'))
            else:
                self.send_json({'error': 'index.html not found'}, 404)

        elif path == '/api/config':
            key = get_api_key()
            templates = get_ashby_templates()
            self.send_json({
                'has_key': bool(key),
                'key_preview': (key[:8] + '...') if key else None,
                'ashby_templates': sorted(templates.keys()),
                'ashby_ready': all(t in templates for t in ('ApiGetCandidatesByCustomFilter', 'ApiGetCandidateProfile')),
                'ashby_has_plan_template': 'ApiFindInterviewPlanWithActivities' in templates,
            })

        elif path == '/api/parker':
            self.send_json(get_parker_data())

        elif path == '/api/parker/refresh':
            try:
                import datetime
                merged_raw = {}
                errors = []
                # Pull all geos that matter for Candidate Labs — merge by company_id
                for geo in ('SF', 'NYC', 'Remote'):
                    data, err = call_parker_mcp_tool(
                        'GetActiveCompaniesWithSignalsTool',
                        {'geo': geo, 'include_remote': geo != 'Remote'}
                    )
                    if err:
                        errors.append(f'{geo}: {err}')
                        continue
                    for co in (data.get('companies', []) if isinstance(data, dict) else []):
                        cid = co.get('company_id')
                        if cid and cid not in merged_raw:
                            merged_raw[cid] = co
                if not merged_raw:
                    self.send_json({'error': 'No companies fetched. ' + '; '.join(errors)}, 500)
                    return
                companies = _transform_parker_companies(list(merged_raw.values()))
                cache_data = {
                    'last_refreshed': datetime.datetime.utcnow().isoformat() + 'Z',
                    'companies': companies,
                    '_source': 'parker_mcp'
                }
                PARKER_CACHE.parent.mkdir(parents=True, exist_ok=True)
                PARKER_CACHE.write_text(json.dumps(cache_data, indent=2))
                self.send_json({'success': True, 'count': len(companies), 'companies': companies, 'last_refreshed': cache_data['last_refreshed']})
            except Exception as e:
                self.send_json({'error': str(e)}, 500)

        elif path == '/api/slack-accepted':
            if SLACK_CACHE.exists():
                try:
                    data = json.loads(SLACK_CACHE.read_text())
                    self.send_json(data)
                except Exception as e:
                    self.send_json({'error': str(e)}, 500)
            else:
                self.send_json({'companies': {}, 'last_updated': None})

        elif path == '/api/slack-insight':
            self.send_json(get_insight_data())

        else:
            self.send_json({'error': 'Not found'}, 404)

    def do_POST(self):
        try:
            body = self.read_body()
        except Exception:
            self.send_json({'error': 'Invalid JSON body'}, 400)
            return

        path = self.path.split('?')[0]

        if path == '/api/config':
            key = body.get('api_key', '').strip()
            if not key:
                self.send_json({'error': 'No API key provided'}, 400)
                return
            save_api_key(key)
            self.send_json({'success': True})

        elif path == '/api/analyze':
            api_key = get_api_key()
            if not api_key:
                self.send_json({'error': 'no_key'}, 401)
                return
            candidate = body.get('candidate', '').strip()
            jd = body.get('jd', '').strip()
            if not candidate:
                self.send_json({'error': 'No candidate text provided'}, 400)
                return
            # Inject today's date so the model computes tenure against the real "present",
            # not its training cutoff. Without this, "Aug 2024 — Present" gets read as
            # ~6 months (cutoff-relative) instead of the actual elapsed time.
            import datetime
            today = datetime.date.today()
            user_msg = (
                f"TODAY'S DATE: {today.isoformat()} ({today.strftime('%B %Y')}).\n"
                f"When computing tenure from a resume, ALWAYS resolve 'Present' / 'Current' / "
                f"'Now' to TODAY'S DATE above. Do NOT use your training cutoff. "
                f"Example: 'Aug 2024 — Present' as of {today.strftime('%B %Y')} = "
                f"{((today.year - 2024) * 12 + today.month - 8)} months of tenure.\n\n"
                f"CANDIDATE:\n{candidate}"
            )
            if jd:
                user_msg += f'\n\nJOB DESCRIPTION:\n{jd}'
            # Enable web search so the model can verify investor/headcount/funding for
            # companies it doesn't fully recognize — prevents "Unknown" defaults and
            # avoids hallucinated investor attributions.
            web_tools = [{'type': 'web_search_20250305', 'name': 'web_search', 'max_uses': 5}]
            raw, err = call_claude(SIGNAL_SYSTEM_PROMPT, user_msg, api_key,
                                   model='claude-haiku-4-5-20251001',
                                   tools=web_tools, timeout=180)
            if err:
                self.send_json({'error': err}, 500)
                return
            parsed, parse_err = parse_json_response(raw)
            self.send_json({'success': True, 'data': parsed, 'raw': raw, 'parse_error': parse_err})

        elif path == '/api/pitch':
            api_key = get_api_key()
            if not api_key:
                self.send_json({'error': 'no_key'}, 401)
                return
            signal_data = body.get('signal_data') or {}
            candidate_notes = body.get('candidate_notes', '').strip()
            companies = body.get('companies', [])
            filters = body.get('filters', {})

            if not signal_data and not candidate_notes:
                self.send_json({'error': 'No candidate data provided'}, 400)
                return

            # Build candidate summary
            if signal_data:
                candidate_section = f"""SIGNAL ANALYSIS:
Name: {signal_data.get('candidate_name', 'Unknown')}
Verdict: {signal_data.get('verdict', '')} — {signal_data.get('verdict_reason', '')}
Level: {signal_data.get('engineering_level', '')} | Bar: {signal_data.get('bar_score', '')}/10 ({signal_data.get('bar_label', '')})
Complexity: {signal_data.get('complexity_type', '')} — {signal_data.get('complexity_notes', '')}
Tech Stack: {', '.join(signal_data.get('tech_stack', []))}
Green Flags: {'; '.join(signal_data.get('green_flags', []))}
Red Flags: {'; '.join(signal_data.get('red_flags', []))}
Best Stages: {', '.join(signal_data.get('best_company_stages', []))}
Best Company Types: {', '.join(signal_data.get('best_company_types', []))}
Roles to Target: {', '.join(signal_data.get('roles_to_target', []))}
One-liner: {signal_data.get('one_liner', '')}
Recruiter Summary: {signal_data.get('recruiter_summary', '')}"""
            else:
                candidate_section = f"CANDIDATE NOTES:\n{candidate_notes}"

            # Add filters
            filter_notes = []
            if filters.get('location'):
                filter_notes.append(f"Candidate location preference: {filters['location']}")
            if filters.get('visa'):
                filter_notes.append(f"Visa status: {filters['visa']}")
            if filters.get('stage'):
                filter_notes.append(f"Stage preference: {filters['stage']}")
            if filters.get('notes'):
                filter_notes.append(f"Additional notes: {filters['notes']}")
            if filter_notes:
                candidate_section += '\n\nFILTERS:\n' + '\n'.join(filter_notes)

            # Build company list
            co_lines = []
            for c in companies[:35]:
                line = f"- {c.get('name', '')}: {c.get('overview', '')} | Categories: {', '.join(c.get('categories', []))} | Location: {', '.join(c.get('locations', []))} | Office: {c.get('office_policy', '')} | Visa: {c.get('visa_support', '')} | Who to pitch: {c.get('who_to_pitch', '')}"
                if c.get('insiders_note'):
                    line += f" | Note: {c['insiders_note']}"
                co_lines.append(line)

            user_msg = f"{candidate_section}\n\nAVAILABLE COMPANIES:\n" + '\n'.join(co_lines)

            raw, err = call_claude(PITCH_SYSTEM_PROMPT, user_msg, api_key)
            if err:
                self.send_json({'error': err}, 500)
                return
            parsed, parse_err = parse_json_response(raw)
            self.send_json({'success': True, 'data': parsed, 'raw': raw, 'parse_error': parse_err})

        elif path == '/api/suggestions':
            api_key = get_api_key()
            if not api_key:
                self.send_json({'error': 'no_key'}, 401)
                return
            signal_data = body.get('signal_data') or {}
            candidate_notes = body.get('candidate_notes', '').strip()
            companies = body.get('companies', [])
            filters = body.get('filters', {})

            if not signal_data and not candidate_notes:
                self.send_json({'error': 'No candidate data provided'}, 400)
                return

            # Build candidate summary. ALWAYS include candidate_notes if present —
            # that's where the recruiter writes motivators ("wants B2C", "burned out
            # on infra, ready for product-facing"), comp expectations, what they're
            # running away from, and other context not captured in signal JSON.
            # Previously notes were skipped whenever signal_data existed, so the
            # suggestions model lost all motivator context.
            if signal_data:
                candidate_section = f"""CANDIDATE SIGNAL:
Name: {signal_data.get('candidate_name', 'Unknown')}
Talent Tier: {signal_data.get('talent_tier', '')} | Verdict: {signal_data.get('verdict', '')} — {signal_data.get('verdict_reason', '')}
Level: {signal_data.get('engineering_level', '')} | Bar: {signal_data.get('bar_score', '')}/10 ({signal_data.get('bar_label', '')})
Complexity: {signal_data.get('complexity_type', '')} — {signal_data.get('complexity_notes', '')}
Tech Stack: {', '.join(signal_data.get('tech_stack', []))}
Green Flags: {'; '.join(signal_data.get('green_flags', []))}
Red Flags: {'; '.join(signal_data.get('red_flags', []))}
Best Stages: {', '.join(signal_data.get('best_company_stages', []))}
Best Company Types: {', '.join(signal_data.get('best_company_types', []))}
Roles to Target: {', '.join(signal_data.get('roles_to_target', []))}
One-liner: {signal_data.get('one_liner', '')}
Recruiter Summary: {signal_data.get('recruiter_summary', '')}"""
                if candidate_notes:
                    candidate_section += (
                        "\n\nRECRUITER NOTES & MOTIVATORS (what they're actually looking for, "
                        "what to avoid, comp/timing/context — weight these heavily for fit):\n"
                        + candidate_notes
                    )
            else:
                candidate_section = f"CANDIDATE NOTES:\n{candidate_notes}"

            # Add filters
            filter_notes = []
            if filters.get('location'):
                filter_notes.append(f"Candidate location: {filters['location']}")
            if filters.get('visa'):
                filter_notes.append(f"Visa status: {filters['visa']}")
            if filters.get('stage'):
                filter_notes.append(f"Stage preference: {filters['stage']}")
            if filters.get('notes'):
                filter_notes.append(f"Additional notes: {filters['notes']}")
            if filter_notes:
                candidate_section += '\n\nFILTERS:\n' + '\n'.join(filter_notes)

            # Pre-filter companies server-side to keep payload small
            stage_pref = filters.get('stage', '')
            location_pref = filters.get('location', '')
            stage_order = ['seed', 'series a', 'series b', 'series c', 'series d', 'series e', 'series f', 'public']
            def min_stage_idx(stages_str):
                min_idx = 999
                for s in stages_str.lower().split(','):
                    s = s.strip()
                    for i, o in enumerate(stage_order):
                        if o in s and i < min_idx:
                            min_idx = i
                return min_idx if min_idx < 999 else -1

            candidate_min_stage = min_stage_idx(stage_pref) if stage_pref else -1

            # Parse freeform location strings like "Seattle (1 yr) — open to relocate to Bay Area or NYC; hybrid"
            # Detect city/region intent via substring search on the full lowercased string, not per-comma tag.
            location_lower = (location_pref or '').lower()
            loc_tags = [l.strip().lower() for l in re.split(r'[,;/]| or | and ', location_pref) if l.strip()] if location_pref else []
            def _has(*needles):
                return any(n in location_lower for n in needles)
            wants_nyc = _has('nyc', 'new york', 'brooklyn', 'manhattan')
            wants_sf = _has('sf', 'san francisco', 'bay area', 'south bay', 'peninsula', 'mountain view', 'palo alto')
            wants_remote = _has('remote', 'anywhere', 'fully distributed')
            wants_seattle = _has('seattle', 'puget')
            wants_la = _has(' la ', 'los angeles', ' la,', ' la;') or location_lower.startswith('la ') or location_lower.endswith(' la')
            wants_boston = _has('boston', 'cambridge,')
            wants_austin = _has('austin')

            def company_passes_location(c):
                if not location_pref.strip():
                    return True
                co_locs = [l.lower() for l in (c.get('locations') or [])]
                co_policy = (c.get('office_policy') or '').lower()
                co_is_remote = 'remote' in co_locs or 'canada' in co_locs or 'remote' in co_policy
                co_has_nyc = any(l in ('nyc', 'new york', 'new york city') for l in co_locs)
                co_has_sf = any(l in ('sf', 'san francisco', 'sf bay peninsula', 'sf bay', 'bay area') for l in co_locs)
                co_has_seattle = 'seattle' in co_locs
                co_has_la = any(l in ('la', 'los angeles') for l in co_locs)
                co_has_boston = any(l in ('boston', 'cambridge') for l in co_locs)
                co_has_austin = 'austin' in co_locs
                # Build the set of "OK city" flags from candidate prefs — ANY hit passes.
                # This is intentionally permissive: when candidate notes mention multiple geos
                # ("Seattle, open to Bay Area or NYC"), all named geos should match.
                pass_flags = []
                if wants_nyc: pass_flags.append(co_has_nyc)
                if wants_sf: pass_flags.append(co_has_sf)
                if wants_seattle: pass_flags.append(co_has_seattle)
                if wants_la: pass_flags.append(co_has_la)
                if wants_boston: pass_flags.append(co_has_boston)
                if wants_austin: pass_flags.append(co_has_austin)
                if wants_remote: pass_flags.append(co_is_remote)
                if pass_flags:
                    # Remote companies always pass IF candidate is open to relocating geos at all
                    # (because remote covers any city pref). Otherwise just check ANY named geo matches.
                    return any(pass_flags) or co_is_remote
                # No recognized geo keyword in candidate prefs — fall back to fuzzy substring across full string.
                # Remote companies always pass through fallback.
                if co_is_remote:
                    return True
                return any(
                    tag and (tag in co_loc or co_loc in tag)
                    for tag in loc_tags
                    for co_loc in co_locs
                    if co_loc not in ('remote', 'canada')
                )

            filtered_companies = []
            for c in companies:
                co_stage = (c.get('funding_stage') or '').lower()
                if candidate_min_stage >= 0:
                    co_stage_idx = next((i for i, o in enumerate(stage_order) if o in co_stage), -1)
                    if co_stage_idx != -1 and co_stage_idx < candidate_min_stage:
                        continue
                if not company_passes_location(c):
                    continue
                filtered_companies.append(c)

            # Rank companies by signal richness (Parker insiders_note length + Slack insight bonus +
            # signal recency). Since Parker now populates rich Accepted/Rejected data for nearly all
            # companies, the old "has Slack insight" binary no longer discriminates — we need a
            # finer-grained score so candidates like Dili (rich Parker junior-acceptance signal) don't
            # get shoved past the LLM cap by alphabetical order.
            insight_data = get_insight_data()
            insight_companies = insight_data.get('companies', {})
            slack_keys_lower = {k.lower() for k in insight_companies}
            def _rank_score(c):
                name = (c.get('name') or '').lower()
                note = c.get('insiders_note') or ''
                score = 0
                # Has-rich-signal flag is binary (500) instead of proportional to length,
                # so a tight 600-char Parker note with a relevant junior-acceptance signal
                # (e.g. Dili) doesn't lose ranking to a verbose 1500-char note about an
                # irrelevant company. The LLM does the actual fit reasoning.
                if 'accepted' in note.lower() and len(note) > 150:
                    score += 500
                # Slack INSIGHT data is an additional independent corroborating source
                if name in slack_keys_lower:
                    score += 500
                # Recency bonus — fresher signals are more current (0–30 days = up to 300)
                age = c.get('signal_age_days')
                if isinstance(age, int):
                    score += max(0, 300 - age * 10)
                return score
            ranked = sorted(filtered_companies, key=_rank_score, reverse=True)
            # Cap at 120 — large enough to keep essentially every geo-matched Parker company
            # in the prompt even for permissive multi-geo searches (NYC + SF + Seattle + remote
            # ≈ entire cache). At ~800 chars per company line this is ~24K tokens, well within
            # the sonnet-4-6 context window. Better to err on inclusion: the LLM filters out
            # bad fits but cannot recover companies that never reach the prompt.
            final_companies = ranked[:120]

            # Build company list with insight data
            co_lines = []
            for c in final_companies:
                name = c.get('name', '')
                line = (f"- {name} [Tier: {c.get('talent_tier', '')}]: {c.get('overview', '')} | "
                        f"Location: {', '.join(c.get('locations', []))} | "
                        f"Office: {c.get('office_policy', '')} | "
                        f"Categories: {', '.join(c.get('categories', []))} | "
                        f"Visa: {c.get('visa_support', '')} | "
                        f"Who to pitch: {c.get('who_to_pitch', '')}")
                if c.get('insiders_note'):
                    line += f" | Parker note: {c['insiders_note']}"
                # Attach insight canvas data if available
                insight_key = next((k for k in insight_companies if k.lower() == name.lower()), None)
                if insight_key:
                    ins = insight_companies[insight_key]
                    hs = ins.get('hiring_signals', {})
                    accepted_skills = '; '.join(hs.get('accepted_skillsets', []))
                    accepted_bg = '; '.join(hs.get('accepted_backgrounds', []))
                    rejected = '; '.join(hs.get('rejected_traits', []))
                    other = ins.get('other_signals', '')
                    sentiment = ins.get('sentiment', '')
                    line += (f" | INSIGHT DATA (from client channel, period {ins.get('period', '')}, sentiment: {sentiment}): "
                             f"Accepted skillsets: {accepted_skills}. "
                             f"Accepted backgrounds: {accepted_bg}. "
                             f"Rejected traits: {rejected}."
                             f"{(' Other signals: ' + other) if other else ''}")
                co_lines.append(line)

            user_msg = f"{candidate_section}\n\nCOMPANIES TO EVALUATE ({len(co_lines)} total):\n" + '\n'.join(co_lines)

            raw, err = call_claude(SUGGESTIONS_SYSTEM_PROMPT, user_msg, api_key, model='claude-sonnet-4-6')
            if err:
                self.send_json({'error': err}, 500)
                return
            parsed, parse_err = parse_json_response(raw)
            self.send_json({'success': True, 'data': parsed, 'raw': raw, 'parse_error': parse_err})

        elif path == '/api/slack-insight/save':
            companies_data = body.get('companies', {})
            import datetime
            existing = get_insight_data()
            existing_companies = existing.get('companies', {})
            existing_companies.update(companies_data)
            cache = {
                'last_updated': datetime.datetime.utcnow().isoformat() + 'Z',
                'companies': existing_companies
            }
            try:
                SLACK_INSIGHT_CACHE.write_text(json.dumps(cache, indent=2))
                self.send_json({'success': True, 'count': len(existing_companies)})
            except Exception as e:
                self.send_json({'error': str(e)}, 500)

        elif path == '/api/gem-sequence':
            api_key = get_api_key()
            if not api_key:
                self.send_json({'error': 'no_key'}, 401)
                return
            role = body.get('role', '').strip()
            location = body.get('location', '').strip()
            companies = body.get('companies', [])
            extra_companies = body.get('extra_companies', [])
            notes = body.get('notes', '').strip()
            if len(companies) < 3:
                self.send_json({'error': '3 companies required'}, 400)
                return
            co_list = '\n'.join([f"- {c}" for c in companies])
            extra_list = '\n'.join([f"- {c}" for c in extra_companies]) if extra_companies else ''
            context = f"Role: {role or 'not specified'}\nLocation: {location or 'not specified'}\nCandidate notes: {notes or 'none'}\n\nPRIMARY companies (feature in all 5 emails):\n{co_list}"
            if extra_list:
                context += f"\n\nADDITIONAL companies to mention briefly in emails 2–5 (1 per email, rotate through them as extra options):\n{extra_list}"
            gem_prompt = '''You are an expert technical recruiter at Candidate Labs writing a 5-email outreach sequence for Gem. Rules:
- Tone: casual, direct, never corporate. "Hey" not "Hi". Never use rockstar/ninja/guru/passionate/disruptive.
- All 5 emails reference the 3 PRIMARY companies naturally (weave them in, don't list dump).
- Emails 2–5 each also briefly mention 1 of the ADDITIONAL companies as a bonus option ("also have a few others that might be worth a look — [Company] is another one...").
- Every email mentions that you personally work with 100+ startups all backed by tier-1 VCs (a16z, Sequoia, General Catalyst, Lightspeed, etc.) — vary the phrasing each time.
- Emails get progressively shorter and more casual. Email 1 is the fullest pitch. Email 5 is 2-3 sentences max.
- Never mention salary or compensation.
- Each email has a different angle: Email 1=value prop, Email 2=social proof/traction, Email 3=specific role hook, Email 4=FOMO/timing, Email 5=easy yes.
- Sign off with "— DJ" every time.
- Return ONLY valid JSON, no markdown: {"emails":[{"subject":"...","body":"..."},{"subject":"...","body":"..."},{"subject":"...","body":"..."},{"subject":"...","body":"..."},{"subject":"...","body":"..."}]}'''
            raw, err = call_claude(gem_prompt, context, api_key)
            if err:
                self.send_json({'error': err}, 500)
                return
            parsed, parse_err = parse_json_response(raw)
            if parsed and 'emails' in parsed:
                self.send_json({'success': True, 'emails': parsed['emails']})
            else:
                self.send_json({'error': 'Failed to parse email sequence', 'raw': raw}, 500)

        elif path == '/api/refresh-sourcing':
            api_key = get_api_key()
            if not api_key:
                self.send_json({'error': 'no_key'}, 401)
                return
            role = body.get('role', 'Backend').strip()
            user_msg = f"Generate a fresh daily sourcing plan for: {role} engineers at VC-backed startups (Seed–Series B), primarily in NYC and SF. Be specific, actionable, and different from generic advice."
            raw, err = call_claude(REFRESH_SOURCING_PROMPT, user_msg, api_key, model='claude-sonnet-4-6')
            if err:
                self.send_json({'error': err}, 500)
                return
            parsed, parse_err = parse_json_response(raw)
            self.send_json({'success': True, 'data': parsed, 'raw': raw, 'parse_error': parse_err})

        elif path == '/api/sync-gdoc':
            url = body.get('url', '').strip()
            if not url:
                self.send_json({'error': 'No URL provided'}, 400)
                return
            try:
                id_match = re.search(r'/document/d/([a-zA-Z0-9_-]+)', url)
                if not id_match:
                    self.send_json({'error': 'Could not parse Google Doc ID from URL'}, 400)
                    return
                doc_id = id_match.group(1)
                ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'

                txt_url = f'https://docs.google.com/document/d/{doc_id}/export?format=txt'
                req = urllib.request.Request(txt_url)
                req.add_header('User-Agent', ua)
                with urllib.request.urlopen(req, timeout=12) as resp:
                    content = resp.read().decode('utf-8', errors='replace')

                # Also fetch HTML to extract hyperlinked LinkedIn URLs
                # (txt export drops anchor hrefs, leaving only display text)
                linkedin_urls = {}
                try:
                    html_url = f'https://docs.google.com/document/d/{doc_id}/export?format=html'
                    req2 = urllib.request.Request(html_url)
                    req2.add_header('User-Agent', ua)
                    with urllib.request.urlopen(req2, timeout=12) as resp2:
                        html = resp2.read().decode('utf-8', errors='replace')

                    from html import unescape
                    # Anchor tags: <a href="...">display</a>
                    for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL):
                        href = unescape(m.group(1))
                        # Unwrap Google's redirect wrapper: ...?q=ACTUAL_URL&...
                        gq = re.match(r'^https?://(?:www\.)?google\.com/url\?q=([^&]+)', href)
                        if gq:
                            href = urllib.parse.unquote(gq.group(1))
                        if 'linkedin.com/in/' not in href.lower():
                            continue
                        # Display text: strip nested tags + entities, collapse whitespace
                        display = re.sub(r'<[^>]+>', '', m.group(2))
                        display = unescape(display).strip()
                        display = re.sub(r'\s+', ' ', display)
                        if not display:
                            continue
                        # Clean trailing punctuation in URL
                        href = re.sub(r'[).,;]+$', '', href)
                        # First occurrence wins
                        key = display.lower()
                        if key not in linkedin_urls:
                            linkedin_urls[key] = href
                except Exception:
                    pass  # html extraction is best-effort

                self.send_json({'success': True, 'content': content.strip(), 'linkedinUrls': linkedin_urls})
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    self.send_json({'error': 'Document not publicly accessible.'}, 403)
                else:
                    self.send_json({'error': f'HTTP error {e.code}'}, 500)
            except Exception as e:
                self.send_json({'error': str(e)}, 500)

        # ─── Ashby integration (session-cookie + curl-paste model) ────────────
        elif path == '/api/ashby-import-curls':
            # One-shot setup: paste any number of curls (the user is expected to copy
            # a few different operations from DevTools → Network). Server splits them,
            # parses each, saves every (operationName, query) it sees as a template,
            # and returns a status summary. Cookie + CSRF are not stored — sync still
            # needs a fresh curl per run because both rotate.
            curl_text = body.get('curl_text') or ''
            if not curl_text.strip():
                self.send_json({'error': 'Paste at least one curl first.'}, 400)
                return
            # Split on lines that start with `curl ` (after any whitespace).
            chunks = []
            buf = []
            for line in curl_text.splitlines():
                if re.match(r'^\s*curl\s+', line) and buf:
                    chunks.append('\n'.join(buf)); buf = []
                buf.append(line)
            if buf: chunks.append('\n'.join(buf))

            templates = get_ashby_templates()
            saved_now = []
            parse_errs = []
            last_session = None  # {cookie, csrf}
            for c in chunks:
                p, err = parse_ashby_curl(c)
                if err or not p:
                    parse_errs.append(err or 'unknown'); continue
                if p.get('cookie') and p.get('csrf'):
                    last_session = {'cookie': p['cookie'], 'csrf': p['csrf']}
                op = p.get('operationName'); q = p.get('query')
                if op and q and templates.get(op) != q:
                    templates[op] = q
                    saved_now.append(op)
            if saved_now:
                save_ashby_templates(templates)
            self.send_json({
                'success': True,
                'curls_seen': len(chunks),
                'templates_saved_now': saved_now,
                'templates_total': sorted(templates.keys()),
                'parse_errors': parse_errs,
                'session_captured': bool(last_session),
            })

        elif path == '/api/ashby-save-template':
            # Save a captured GraphQL query template. Body: {curl_text}.
            # Used during one-time setup to teach the server the exact query strings
            # for the 2–3 operations we need. The server extracts {operationName, query}
            # from the pasted curl body and persists them.
            curl_text = body.get('curl_text') or ''
            parsed, perr = parse_ashby_curl(curl_text)
            if perr or not parsed:
                self.send_json({'error': f'Could not parse curl: {perr or "no fields found"}'}, 400)
                return
            op = parsed.get('operationName')
            q = parsed.get('query')
            if not op or not q:
                self.send_json({'error': 'curl body did not contain operationName + query (not a GraphQL request?)'}, 400)
                return
            templates = get_ashby_templates()
            templates[op] = q
            save_ashby_templates(templates)
            self.send_json({
                'success': True,
                'operationName': op,
                'templates_saved': sorted(templates.keys()),
                'example_variables': parsed.get('variables'),
            })

        elif path == '/api/ashby-templates':
            # Return what query templates are already saved (names only).
            self.send_json({'success': True, 'templates': sorted(get_ashby_templates().keys())})

        elif path == '/api/sync-ashby':
            # LOOKUP MODE — never imports candidates we don't already have.
            # Body: {
            #   curl_text:  "curl 'https://app.ashbyhq.com/api/graphql?op=...' -H 'cookie: …' …"
            #               (any recent Ashby request — used only for cookie + CSRF)
            #   candidates: [{id, name, email?, linkedin?, ashbyId?}]
            # }
            # For each local candidate: search → profile → (optional) interview plan.
            curl_text = body.get('curl_text') or ''
            local = body.get('candidates') or []
            if not isinstance(local, list) or len(local) == 0:
                self.send_json({'error': 'No local candidates provided'}, 400)
                return
            parsed, perr = parse_ashby_curl(curl_text)
            if perr or not parsed:
                self.send_json({'error': f'Could not parse session curl: {perr or "missing fields"}'}, 400)
                return
            cookie = parsed['cookie']
            csrf = parsed['csrf']
            if not csrf:
                self.send_json({'error': 'No x-csrf-token in pasted curl. Pick a curl from a POST /api/graphql request in DevTools — those carry the CSRF header.'}, 400)
                return

            templates = get_ashby_templates()
            search_q = templates.get('ApiGetCandidatesByCustomFilter')
            profile_q = templates.get('ApiGetCandidateProfile')
            plan_q = templates.get('ApiFindInterviewPlanWithActivities')  # optional

            # If the session curl itself is one of the operations we don't have yet,
            # opportunistically capture it as a template.
            captured = []
            if parsed.get('operationName') and parsed.get('query'):
                op = parsed['operationName']
                if op not in templates:
                    templates[op] = parsed['query']
                    save_ashby_templates(templates)
                    captured.append(op)
                    if op == 'ApiGetCandidatesByCustomFilter': search_q = parsed['query']
                    elif op == 'ApiGetCandidateProfile':       profile_q = parsed['query']
                    elif op == 'ApiFindInterviewPlanWithActivities': plan_q = parsed['query']

            if not search_q or not profile_q:
                missing = [n for n,q in [('ApiGetCandidatesByCustomFilter', search_q),
                                          ('ApiGetCandidateProfile', profile_q)] if not q]
                self.send_json({
                    'error': 'missing_templates',
                    'missing': missing,
                    'message': (
                        'First-time setup: paste one curl per missing operation via the '
                        '"Capture query" button. You only need to do this once per machine.'
                    ),
                }, 400)
                return

            # ── Per-candidate work ────────────────────────────────────────────
            def search(name):
                vars_ = {'searchTerm': name, 'extraFields': []}
                data, err = call_ashby_graphql('ApiGetCandidatesByCustomFilter', vars_, search_q, cookie, csrf)
                if err or not data: return [], err
                # Response shape varies — defensive walk.
                d = data.get('data') or {}
                root = d.get('result') or d.get('candidatesByCustomFilter') or d.get('candidates') or {}
                if isinstance(root, list): return root, None
                return (root.get('results') or root.get('nodes') or []), None

            def profile(candidate_id):
                vars_ = {'candidateId': candidate_id}
                data, err = call_ashby_graphql('ApiGetCandidateProfile', vars_, profile_q, cookie, csrf)
                if err or not data: return None, err
                d = data.get('data') or {}
                return (d.get('candidate') or d.get('candidateProfile')
                        or d.get('result') or d.get('node') or d), None

            plan_cache = {}
            def plan_progress(interview_plan_id, current_stage_id, current_stage_title):
                """Return 'X/Y' string, or '' if we can't compute."""
                if not plan_q or not interview_plan_id:
                    return ''
                if interview_plan_id in plan_cache:
                    stages = plan_cache[interview_plan_id]
                else:
                    vars_ = {'interviewPlanId': interview_plan_id}
                    data, err = call_ashby_graphql('ApiFindInterviewPlanWithActivities', vars_, plan_q, cookie, csrf)
                    if err or not data: return ''
                    d = data.get('data') or {}
                    plan = (d.get('interviewPlan') or d.get('result') or d.get('node') or {})
                    stages = (plan.get('interviewStages') or plan.get('stages')
                              or plan.get('orderedInterviewStages') or [])
                    plan_cache[interview_plan_id] = stages
                if not stages: return ''
                total = len(stages)
                idx = None
                for i, s in enumerate(stages):
                    if (current_stage_id and s.get('id') == current_stage_id) or \
                       (current_stage_title and (s.get('title') or '').strip().lower() == current_stage_title.strip().lower()):
                        idx = i; break
                if idx is None: return ''
                return f'{idx+1}/{total}'

            def find_match(local_c, results):
                """Pick the best of N search hits using email > exact name."""
                if not results: return None
                if len(results) == 1: return results[0]
                email = (local_c.get('email') or '').strip().lower()
                name = (local_c.get('name') or '').strip().lower()
                if email:
                    for r in results:
                        for e in (r.get('emailAddresses') or []):
                            if (e.get('value') or '').strip().lower() == email:
                                return r
                if name:
                    exact = [r for r in results if (r.get('name') or '').strip().lower() == name]
                    if len(exact) == 1: return exact[0]
                return None  # ambiguous — skip rather than guess

            matches = []
            unmatched = []
            errors = []
            for lc in local:
                if not isinstance(lc, dict) or not lc.get('id') or not lc.get('name'):
                    continue
                # 1) Search by name
                try:
                    results, serr = search(lc['name'])
                except Exception as e:
                    errors.append({'localId': lc['id'], 'error': f'search threw: {e}'})
                    continue
                if serr:
                    errors.append({'localId': lc['id'], 'error': f'search: {serr}'})
                ac = find_match(lc, results or [])
                if not ac:
                    unmatched.append({'localId': lc['id'], 'name': lc['name'], 'hits': len(results or [])})
                    continue
                # 2) Pull profile
                try:
                    prof, perr = profile(ac.get('id'))
                except Exception as e:
                    errors.append({'localId': lc['id'], 'error': f'profile threw: {e}'})
                    continue
                if perr or not prof:
                    errors.append({'localId': lc['id'], 'error': f'profile: {perr or "empty"}'})
                    continue
                # 3) Shape applications + progress
                apps_out = []
                for app in (prof.get('applications') or []):
                    status = (app.get('status') or '').lower()
                    if status and status not in ('active', 'open', ''):
                        continue
                    cur_stage = app.get('currentInterviewStage') or {}
                    job = app.get('job') or {}
                    brand = (job.get('organizationBrand') or {}).get('name') or ''
                    plan = app.get('interviewPlan') or {}
                    progress = plan_progress(plan.get('id'),
                                              cur_stage.get('id'),
                                              cur_stage.get('title') or '')
                    apps_out.append({
                        'co': brand or job.get('title') or 'Unknown',
                        'jobTitle': job.get('title') or '',
                        'st': cur_stage.get('title') or status or '',
                        'progress': progress,  # e.g. "3/4"
                        'n': (app.get('updatedAt') or '')[:10],
                        'applicationId': app.get('id'),
                        'status': app.get('status') or '',
                    })
                # Backfill contact info opportunistically
                linkedin = ''
                for link in (prof.get('socialLinks') or ac.get('socialLinks') or []):
                    if 'linkedin.com' in (link.get('url') or '').lower():
                        linkedin = link.get('url'); break
                email = ''
                for e in (prof.get('emailAddresses') or ac.get('emailAddresses') or []):
                    if e.get('value'):
                        email = e.get('value'); break
                matches.append({
                    'localId': lc['id'],
                    'ashbyId': ac.get('id'),
                    'ashbyName': prof.get('name') or ac.get('name') or '',
                    'email': email,
                    'linkedin': linkedin,
                    'applications': apps_out,
                })

            self.send_json({
                'success': True,
                'requested': len(local),
                'matched': len(matches),
                'unmatched_count': len(unmatched),
                'matches': matches,
                'unmatched': unmatched,
                'errors': errors,
                'templates_captured': captured,
                'has_plan_template': bool(plan_q),
            })

        elif path == '/api/ats-suggest':
            api_key = get_api_key()
            if not api_key:
                self.send_json({'error': 'no_key'}, 401)
                return
            candidate = body.get('candidate', {})
            if not candidate:
                self.send_json({'error': 'No candidate data'}, 400)
                return
            subs = candidate.get('subs', [])
            sub_lines = '\n'.join(f"  - {s.get('co','?')}: {s.get('st','?')}{(' — '+s.get('n')) if s.get('n') else ''}" for s in subs) or '  (none)'
            system = (
                "You are an expert technical recruiter assistant. Given a candidate's profile, notes, and pipeline status, "
                "generate actionable, specific suggestions for the recruiter. Focus on: (1) next best companies to target based on "
                "profile and what's already been tried, (2) talking points or positioning angles for upcoming conversations, "
                "(3) specific follow-up actions given current pipeline stage, (4) any risks or watch-outs. "
                "Be concise, bullet-pointed, and recruiter-ready. No fluff."
            )
            user_msg = f"""CANDIDATE: {candidate.get('name','?')}
HEADLINE: {candidate.get('headline','')}
ROLE TARGET: {candidate.get('role','')}
LOCATION: {candidate.get('loc','')} | PREF: {candidate.get('pref','')}
COMP: {candidate.get('comp','')}
STACK: {', '.join(candidate.get('stack',[]))}
PIPELINE STAGE: {candidate.get('ps','')}
AUTH: {candidate.get('auth','')}
OTHER PROCESSES: {candidate.get('other','')}
INTERVIEW DATE: {candidate.get('interviewDate','not set')}

INITIAL NOTES:
{candidate.get('notes','')}

MY CALL NOTES:
{candidate.get('callNotes','(none)')}

SUBMISSIONS SO FAR:
{sub_lines}

Generate specific, actionable recruiter suggestions."""
            raw, err = call_claude(system, user_msg, api_key)
            if err:
                self.send_json({'error': err}, 500)
                return
            self.send_json({'success': True, 'text': raw})

        elif path == '/api/parker/save':
            companies = body.get('companies', [])
            import datetime
            cache_data = {
                'last_refreshed': datetime.datetime.utcnow().isoformat() + 'Z',
                'companies': companies
            }
            try:
                PARKER_CACHE.parent.mkdir(parents=True, exist_ok=True)
                PARKER_CACHE.write_text(json.dumps(cache_data, indent=2))
                self.send_json({'success': True, 'count': len(companies)})
            except Exception as e:
                self.send_json({'error': str(e)}, 500)

        elif path == '/api/help-chat':
            api_key = get_api_key()
            if not api_key:
                self.send_json({'error': 'no_key'}, 401)
                return
            mode = (body.get('mode') or 'ask').strip()  # 'ask' | 'locate' | 'debug'
            question = (body.get('question') or '').strip()
            page_ctx = body.get('page_context') or {}  # candidate, tab, visible_companies, etc.
            history = body.get('history') or []  # [{role, content}, ...] last 6 turns max
            if not question:
                self.send_json({'error': 'No question provided'}, 400)
                return

            # Build context block — kept small on purpose
            ctx_parts = []
            if page_ctx.get('tab'):
                ctx_parts.append(f"Current tab: {page_ctx['tab']}")
            if page_ctx.get('candidate'):
                cand = page_ctx['candidate']
                # If candidate came from a chat upload, label it differently and pin it as the focus
                src = page_ctx.get('candidate_source')
                if src == 'uploaded_in_chat':
                    label = (
                        "🎯 FOCUSED CANDIDATE (uploaded into this chat — this is the candidate the "
                        "recruiter is asking about, regardless of what tab is open in the browser):"
                    )
                else:
                    label = "Candidate on screen (full object):"
                if isinstance(cand, dict):
                    try:
                        cand_json = json.dumps(cand, default=str)[:6000]
                    except Exception:
                        cand_json = str(cand)[:6000]
                    ctx_parts.append(f"{label}\n{cand_json}")
                else:
                    ctx_parts.append(f"{label} {str(cand)[:1000]}")
                # Attach the full resume text for chat-uploaded candidates so follow-ups
                # ("what's their stack?", "pull more detail") have the source material
                if page_ctx.get('candidate_resume_text'):
                    ctx_parts.append(
                        "Resume text for FOCUSED CANDIDATE:\n"
                        + str(page_ctx['candidate_resume_text'])[:12000]
                    )
            if page_ctx.get('visible_companies'):
                vc = page_ctx['visible_companies'][:25]
                ctx_parts.append("Visible company suggestions on screen: " + '; '.join(
                    f"{c.get('company','?')} ({c.get('fit_score','?')}/10)" if isinstance(c, dict) else str(c)
                    for c in vc
                ))
            # Full ATS roster for cross-candidate queries
            # ("find all research engineers", "who's senior and SF-based", etc.)
            if page_ctx.get('ats_roster'):
                roster = page_ctx['ats_roster']
                active = [c for c in roster if c.get('status') != 'archived' and c.get('ps') != 'placed']
                archived = [c for c in roster if c.get('status') == 'archived' or c.get('ps') == 'closed']
                placed = [c for c in roster if c.get('ps') == 'placed']
                # Compact NAME INDEX first — guarantees EVERY candidate name is visible
                # even if the detailed JSON gets truncated. Bug: at 89 candidates the
                # detailed JSON was getting cut at 30K chars, chopping candidates off
                # the end and making the bot say "Dhruv Patel not in roster" when he was.
                def _stat(c):
                    if c.get('ps') == 'placed': return 'placed'
                    if c.get('status') == 'archived' or c.get('ps') == 'closed': return 'archived'
                    return 'active'
                name_index = '\n'.join(
                    f"  - {c.get('name','?')} [{_stat(c)}] (id={c.get('id','?')})"
                    for c in roster
                )
                try:
                    roster_json = json.dumps(roster, default=str)
                except Exception:
                    roster_json = str(roster)
                ctx_parts.append(
                    f"FULL ATS ROSTER ({len(roster)} candidates: {len(active)} active, "
                    f"{len(archived)} archived, {len(placed)} placed).\n\n"
                    f"=== NAME INDEX (EVERY candidate — fuzzy-match against this BEFORE saying 'not found') ===\n"
                    f"{name_index}\n=== END NAME INDEX ===\n\n"
                    f"DETAILED ROSTER (headline, role, loc, comp, auth, stack, signal_summary — "
                    f"may be truncated for very large rosters; if a name appears in the NAME INDEX "
                    f"above but is missing detail here, that candidate IS in the roster — answer based "
                    f"on what you have or ask the user to open them):\n{roster_json[:60000]}"
                )
            if page_ctx.get('extra'):
                ctx_parts.append(f"Extra: {str(page_ctx['extra'])[:1000]}")

            # Server-side attach: load Parker cache + Slack insight when UI requests it.
            # This is the data the suggestions endpoint uses, so the bot can answer questions
            # like "why wasn't X included" or "what companies fit a B2C candidate".
            if page_ctx.get('want_full_company_data') and mode != 'locate':
                try:
                    parker = get_parker_data()
                    companies = parker.get('companies', []) or []
                    insight_data = get_insight_data()
                    insight_companies = insight_data.get('companies', {}) or {}
                    co_lines = []
                    for c in companies:
                        name = c.get('name', '')
                        line = (
                            f"- {name} | tier={c.get('talent_tier','?')} | "
                            f"stage={c.get('funding_stage','?')} | "
                            f"locations={', '.join(c.get('locations',[]) or [])} | "
                            f"office={c.get('office_policy','')} | "
                            f"roles={', '.join(c.get('active_searches',[]) or [])} | "
                            f"categories={', '.join(c.get('categories',[]) or [])}"
                        )
                        note = c.get('insiders_note') or ''
                        if note:
                            line += f" | note: {note[:400]}"
                        # Attach insight data if present
                        ikey = next((k for k in insight_companies if k.lower() == name.lower()), None)
                        if ikey:
                            ins = insight_companies[ikey]
                            hs = ins.get('hiring_signals', {}) or {}
                            line += (
                                f" | INSIGHT: accepted=[{'; '.join(hs.get('accepted_skillsets',[]))[:200]}] "
                                f"bg=[{'; '.join(hs.get('accepted_backgrounds',[]))[:200]}] "
                                f"rejected=[{'; '.join(hs.get('rejected_traits',[]))[:200]}]"
                            )
                        co_lines.append(line)
                    ctx_parts.append(
                        f"PARKER CACHE ({len(co_lines)} companies, last_refreshed={parker.get('last_refreshed','?')}):\n"
                        + '\n'.join(co_lines)
                    )
                    # Also include the live ranking rules so the bot can explain exclusions
                    ctx_parts.append(
                        "SUGGESTIONS RANKING RULES (from server.py — these are why companies get included/excluded):\n"
                        + SUGGESTIONS_SYSTEM_PROMPT
                    )
                except Exception as e:
                    ctx_parts.append(f"(Could not attach Parker cache: {e})")

            # Mode-specific system prompt + auto-attached code for debug mode
            if mode == 'locate':
                system = (
                    "You are an in-app navigation helper for a local recruiter dashboard. "
                    "The user wants to FIND something already on the page (a candidate, a company, "
                    "a section). Reply with ONE JSON object only — no prose, no markdown — using this schema: "
                    '{"answer": "1-2 sentence plain text answer for the user", '
                    '"action": {"type": "scroll_to" | "filter" | "switch_tab" | "none", '
                    '"target": "css selector or text to match", '
                    '"tab": "Profile & Notes" | "Pipeline" | "Suggestions" | null}}. '
                    "Use action.type='none' if you cannot map the request to a UI action."
                )
            elif mode == 'debug':
                # Attach source excerpts so the bot can point at file:line.
                # Only attach files the user explicitly names OR a small index of route names.
                code_snippets = []
                try:
                    server_text = (SCRIPT_DIR / 'server.py').read_text()
                    # Build a tiny route index so the bot knows where things live
                    route_lines = []
                    for i, ln in enumerate(server_text.splitlines(), 1):
                        s = ln.strip()
                        if s.startswith("elif path ==") or s.startswith("if path ==") or s.startswith("def "):
                            route_lines.append(f"  server.py:{i}: {s[:140]}")
                    code_snippets.append("server.py route/function index (line numbers are authoritative):\n" + '\n'.join(route_lines[:200]))
                    # If question mentions a specific endpoint, attach ~40 lines around it
                    q_lower = question.lower()
                    for needle in ['/api/suggestions', '/api/parker', '/api/analyze', '/api/pitch',
                                   '/api/help-chat', '/api/ats-suggest', '/api/gem-sequence',
                                   '/api/refresh-sourcing', '/api/slack-insight', '/api/sync-gdoc']:
                        if needle in q_lower:
                            lines = server_text.splitlines()
                            for i, ln in enumerate(lines):
                                if needle in ln and "path ==" in ln:
                                    start = max(0, i)
                                    end = min(len(lines), i + 80)
                                    excerpt = '\n'.join(f"{j+1}: {lines[j]}" for j in range(start, end))
                                    code_snippets.append(f"server.py excerpt for {needle}:\n{excerpt}")
                                    break
                except Exception as e:
                    code_snippets.append(f"(could not load server.py: {e})")
                if code_snippets:
                    ctx_parts.append('\n\n'.join(code_snippets))

                # Recent server.log tail
                try:
                    log_path = SCRIPT_DIR / 'server.log'
                    if log_path.exists() and log_path.stat().st_size > 0:
                        log_text = log_path.read_text(errors='replace')
                        tail = log_text[-3000:]
                        ctx_parts.append(f"Recent server.log tail:\n{tail}")
                except Exception:
                    pass

                system = (
                    "You are a code-aware debugging assistant for a SINGLE-USER local dashboard "
                    "(server.py + index.html). The user will describe a bug or unexpected behavior. "
                    "Your job: (1) identify the likely root cause, (2) cite the exact file:line "
                    "(e.g. server.py:186), (3) propose a minimal diff the user can paste into "
                    "Claude Code to apply — do NOT pretend you applied it. Be concise. If unsure, "
                    "say what additional info you'd need. Use markdown code blocks for the diff."
                )
            else:  # 'ask'
                system = (
                    "You are an in-app help assistant for a senior technical recruiter at Candidate Labs "
                    "using a local candidate dashboard built on Parker CRM data + Slack insight caches. "
                    "You have access to: the candidate currently on screen (if any), the FULL ATS ROSTER "
                    "(every candidate the recruiter has tracked — active, archived, and placed — with "
                    "their headline, role, location, stack, and signal tier/bar/verdict when available), "
                    "the full Parker company cache (every TT4/TT5 client with locations, roles, hiring "
                    "notes, and Slack insight), and the live ranking rules used by the Suggestions tab. "
                    "When the user asks about 'my candidates', 'my ATS', 'find candidates who…', 'go through "
                    "all my candidates', 'include archived', etc. — use the FULL ATS ROSTER, not just the "
                    "candidate currently on screen. Scan the actual roster and name specific people by name.\n\n"
                    "NAME-IN-QUESTION RULE (CRITICAL): If the user mentions a person's name in their question "
                    "(e.g. 'find opportunities for dhruv patel', 'why isn't owner a fit for jack?', 'is wendy "
                    "TT4?', 'show me dhruv's pipeline'), you MUST resolve that name against the FULL ATS ROSTER "
                    "BEFORE saying you can't find them. Do FUZZY case-insensitive matching:\n"
                    "  - Exact match (case-insensitive) → use that candidate.\n"
                    "  - First-name only (e.g. 'dhruv') → if exactly one roster entry matches, use it.\n"
                    "  - Last-name only → same rule.\n"
                    "  - Partial / nickname (e.g. 'Mike' → 'Michael Chen') → if exactly one plausible match, use it. If multiple, list them and ask which.\n"
                    "  - Typo / 1-char-off → still try to match (Levenshtein-style — 'dhrvu' ≈ 'Dhruv', 'jak' ≈ 'Jack').\n"
                    "Only say 'not found' if NO plausible match exists across the ENTIRE roster (active + archived + placed). "
                    "When you resolve a name from the question, ALSO answer the question for that candidate — "
                    "don't make the recruiter re-ask. The candidate currently on screen is a HINT for who they mean "
                    "if the question is vague ('this candidate', 'them'), but a named candidate in the question "
                    "ALWAYS wins over the on-screen one.\n\n"
                    "Answer ANY question the recruiter asks — "
                    "open-ended is fine. Examples you should handle well: "
                    "'why wasn't Owner included for Jack?' (cite ranking rules + candidate tier/bar), "
                    "'this candidate wants B2C, what fits?' (scan the Parker cache for B2C companies + tier match), "
                    "'who hires Rails engineers?', 'what's the comp ceiling at Klarity?', 'is Vercel TT5?'. "
                    "Always reason from the actual Parker cache + ranking rules — not vague impressions. "
                    "Cite specific companies by name and call out tier/location/role fit explicitly. "
                    "When excluding companies, name the rule (e.g. 'TT5 client, candidate is bar-7 TT4 → blocked by rule #2'). "
                    "Be concise but thorough — recruiter is in a hurry and wants the answer, not preamble. "
                    "Use markdown (bold, bullets) freely. If you genuinely don't have the data, say so.\n\n"
                    "OUTPUT FORMAT RULE (CRITICAL — DO NOT VIOLATE):\n"
                    "NEVER output a JSON object or JSON array as your answer (no ```json blocks, no raw `{\"suggestions\":...}`, "
                    "no `[{...},{...}]` lists, no key/value dumps). The recruiter is reading this in a chat window, not parsing it. "
                    "When recommending companies, write a SHORT markdown list — one bullet per company with the company name in **bold**, "
                    "then a 1-line reason. Example of what TO DO:\n"
                    "  - **Vapi** (Series B, SF) — real-time voice AI infra, ML Infra role wants Python/Go/Kubernetes. Confirm remote eligibility.\n"
                    "  - **Black Forest Labs** (Series B) — ML infra, Python/Bash/Go/Kubernetes stack matches.\n"
                    "Never wrap the answer in a code fence. Never include keys like `fit_score`, `funding_stage`, `location_status`, `why_match`, "
                    "`insight_summary`, `watch_out` as JSON fields — fold any relevant info into the prose. The ONLY structured output you may emit "
                    "is the explicit `ats-add` block described below, and ONLY when the recruiter explicitly asked to add a candidate.\n\n"
                    "ADD-TO-ATS ACTION:\n"
                    "When the recruiter asks you to ADD a candidate to the ATS (phrases like 'add to ATS', "
                    "'add them to the ATS', 'use the info I gave you and add', 'create the candidate', "
                    "'log this candidate', 'save them to ATS'), you MUST end your response with a fenced "
                    "code block tagged `ats-add` containing a JSON object with the candidate fields you "
                    "extracted from the conversation. Schema (omit any field you don't have):\n"
                    "```ats-add\n"
                    "{\n"
                    '  "name": "Full Name",\n'
                    '  "headline": "1-line summary (e.g. \'Backend/infra engineer, distributed systems, prod ML\')",\n'
                    '  "role": "Target role (e.g. \'Backend / Infrastructure\')",\n'
                    '  "loc": "Location (e.g. \'Palo Alto / SF Bay Peninsula\')",\n'
                    '  "comp": "Comp expectation (e.g. \'$250K+\')",\n'
                    '  "auth": "Work auth (e.g. \'Green Card\' / \'US Citizen\' / \'needs H1B\')",\n'
                    '  "pref": "Office preference (e.g. \'hybrid SF\' / \'fully remote\')",\n'
                    '  "stack": ["Python", "Go", "Kubernetes"],\n'
                    '  "ps": "new",\n'
                    '  "notes": "Any other context the recruiter shared — paste verbatim, not summarized",\n'
                    '  "resume_text": "If a resume/profile was shared in the conversation, paste the full text here so signal analysis can run"\n'
                    "}\n"
                    "```\n"
                    "Above the fenced block, briefly summarize what you're adding (1-2 sentences) so the "
                    "recruiter can verify before clicking the button. Do NOT speculate fields — only include "
                    "what was actually shared. Do NOT run any ranking — the UI handles that. After the user "
                    "clicks the Add button, the UI runs signal analysis automatically. Use this action ONLY "
                    "when the recruiter explicitly asks to add/save/create — not when they ask 'who fits?'."
                )

            # Compose user message: history + context + current question
            user_msg_parts = []
            if history:
                hist_text = '\n'.join(
                    f"{(h.get('role') or 'user').upper()}: {str(h.get('content',''))[:600]}"
                    for h in history[-6:]
                )
                user_msg_parts.append(f"PRIOR TURNS:\n{hist_text}")
            if ctx_parts:
                user_msg_parts.append("PAGE CONTEXT:\n" + '\n\n'.join(ctx_parts))
            user_msg_parts.append(f"USER QUESTION:\n{question}")
            user_msg = '\n\n'.join(user_msg_parts)

            raw, err = call_claude(system, user_msg, api_key, model='claude-sonnet-4-6')
            if err:
                self.send_json({'error': err}, 500)
                return
            resp = {'success': True, 'mode': mode, 'text': raw}
            if mode == 'locate':
                parsed, parse_err = parse_json_response(raw)
                if parsed:
                    resp['action'] = parsed.get('action')
                    resp['text'] = parsed.get('answer') or raw
                else:
                    resp['parse_error'] = parse_err
            self.send_json(resp)

        else:
            self.send_json({'error': 'Not found'}, 404)


# ─── Main ────────────────────────────────────────────────────────────────────────

def open_browser():
    time.sleep(1.2)
    webbrowser.open(f'http://localhost:{PORT}')

if __name__ == '__main__':
    print(f'\n  Candidate Labs Recruiter UI')
    print(f'  Running at: http://localhost:{PORT}\n')

    key = get_api_key()
    if key:
        print(f'  API key: {key[:8]}... (found)')
    else:
        print(f'  API key: not set — open the app and go to Settings')

    print(f'  Opening browser...\n')

    socketserver.TCPServer.allow_reuse_address = True
    threading.Thread(target=open_browser, daemon=True).start()

    with socketserver.TCPServer(('', PORT), RecruiterHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n  Server stopped.')
