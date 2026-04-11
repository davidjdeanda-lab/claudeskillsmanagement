# Claude Skills & Memory Transfer Guide

## How to Set Up Your New Claude Account

### Step 1: Add Memory Edits

Go to your new Claude account and paste these one at a time in conversation, asking Claude to "remember" each one. Or open Settings → Memory and add them manually.

```
1. "My name is David. I'm a senior technical recruiter at SingleSprout, placing engineers at VC-backed startups (Seed–Series D). Clients include Perplexity, Decagon, Anthropic."
2. "I source across Backend, Frontend, Fullstack, Infra/DevOps, ML, AI, Data Engineering, PM, Product Design, and FDE roles — primarily NYC and SF."
3. "I'm based on the West Coast (LAX/SNA area) and have a girlfriend."
4. "I trade stocks on Schwab (NVDA, AVGO) and crypto on Robinhood (BTC). Small starter portfolio, ~$500 budget. Morning brief routine at 6:30 AM PT."
5. "I prefer casual, direct, action-oriented communication. 'Hey' not 'Hi'. No corporate fluff. Don't ask clarifying questions — just execute."
6. "When I upload a resume or paste a LinkedIn profile, run Signal candidate analysis automatically. When I ask for a sourcing playbook, build it immediately."
7. "I built an AI-powered SingleSprout recruiting app as a React artifact using claude-sonnet-4-20250514 with two modules: Sourcing Playbook and Signal (candidate analysis)."
8. "For artifacts using the Anthropic API, always use model string claude-sonnet-4-20250514. Send PDFs as native document blocks."
9. "I'm transitioning to a new job. My 401k rollover/merge is pending — old provider TBD, new provider TBD."
```

### Step 2: Upload Skills

Your new Claude account needs these skill files uploaded. Each skill has a SKILL.md file and a references/ subdirectory.

**Skill 1: david-finance**
- `david-finance/SKILL.md` — Portfolio daily brief + 401k advisor
- `david-finance/references/portfolio-data.md` — Current positions and financial data

**Skill 2: singlesprout-recruiter**
- `singlesprout-recruiter/SKILL.md` — Signal candidate analysis + Sourcing playbook
- `singlesprout-recruiter/references/signal-analysis.md` — Signal scoring rubric, Find More Like This, Pitch Builder, LI Brief prompts
- `singlesprout-recruiter/references/sourcing-data.md` — All 10 roles: signals, booleans, channels, VC targets, drip generation

### Step 3: Verify

Start a new conversation and test:
- "Run my portfolio" → should trigger david-finance skill
- "Build me a backend search" → should trigger singlesprout-recruiter skill
- "Analyze this candidate" + upload a resume → should trigger Signal

---

## File Inventory

```
transfer/
├── TRANSFER-GUIDE.md          ← You're reading this
├── david-finance/
│   ├── SKILL.md               ← Finance skill definition
│   └── references/
│       └── portfolio-data.md  ← Your current positions
└── singlesprout-recruiter/
    ├── SKILL.md               ← Recruiting skill definition
    └── references/
        ├── signal-analysis.md ← Candidate analysis framework
        └── sourcing-data.md   ← All role data, booleans, targets
```
