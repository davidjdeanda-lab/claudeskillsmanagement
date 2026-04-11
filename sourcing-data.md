# Sourcing Playbook Reference Data

## Table of Contents
1. [School Context by Role](#school-context-by-role)
2. [Role Data](#role-data) — Signals, niche channels, booleans, outreach tips (all 10 roles)
3. [VC-Backed Target Companies](#vc-backed-target-companies) — Per-role poaching targets
4. [Email Drip Generation](#email-drip-generation) — System prompt and rules

---

## School Context by Role

When generating booleans or briefs, always include the appropriate school list for the role.

**Backend:** Top-tier systems programs: MIT, Stanford, CMU, UC Berkeley, UIUC, Georgia Tech, Cornell, University of Washington, Princeton, Caltech, Purdue, Michigan, UT Austin, Virginia Tech, Stony Brook, University of Maryland, Wisconsin, UCSD. Canadian: University of Waterloo, University of Toronto, UBC.

**Frontend:** Broader top-100 CS programs all relevant. Also: design schools with strong HCI/CS overlap (RISD, Parsons, SVA). Bootcamp grads with strong portfolios (Hack Reactor, App Academy) are highly viable.

**Fullstack:** All strong CS programs relevant. Canadian: Waterloo, Toronto, UBC. Startup-ready signal: self-taught engineers with strong GitHub/side projects, YC alumni, founding engineers.

**Infrastructure / DevOps:** Systems/networking programs: MIT, Stanford, CMU, UC Berkeley, UIUC, Georgia Tech, Cornell, UW, Purdue, Michigan, UT Austin, Virginia Tech. Canadian: Waterloo, Toronto, UBC.

**ML Engineer:** PhD programs matter most: MIT, Stanford, CMU, UC Berkeley, UW, Cornell, Princeton, Caltech, UIUC, Georgia Tech, UCSD, Columbia, NYU, Michigan, UCLA. Canadian: Waterloo, Toronto (Vector Institute), UBC.

**AI Engineer:** Strong CS programs all relevant: MIT, Stanford, CMU, UC Berkeley, UIUC, Georgia Tech, Cornell, UW, Princeton, Caltech, Northeastern, NYU, Columbia, Michigan, UCLA, UCSD. Canadian: Waterloo, Toronto, UBC.

**Data Engineer:** Strong quantitative programs: MIT, Stanford, CMU, UC Berkeley, UIUC, Georgia Tech, Michigan, Cornell, UT Austin, UMass Amherst, UW. Canadian: Waterloo, Toronto, UBC.

**Forward Deployed Engineer:** Strong CS programs with a bias toward engineers who've worked at customer-facing or solutions engineering roles: MIT, Stanford, CMU, UC Berkeley, UIUC, Georgia Tech, Cornell, UW, Michigan, UT Austin. Canadian: Waterloo, Toronto, UBC. Non-traditional backgrounds highly viable — bootcamps, self-taught, liberal arts + CS double major.

**Product Manager:** Top MBAs: Stanford, Harvard, Wharton, MIT Sloan, Kellogg, Booth, Columbia, Tuck, Ross, Fuqua, Cornell Johnson, Haas. Strong undergrads: MIT, Stanford, Berkeley, Cornell, Duke, Princeton, Yale, Michigan, Penn, Northwestern, Brown.

**Product Designer:** Top design programs: RISD, Parsons, Carnegie Mellon, SVA, ArtCenter, SCAD, Pratt. HCI programs: Stanford, MIT, Cornell, Michigan, Georgia Tech, UCSD, UCLA, UW, CMU. Canadian: Emily Carr, OCAD University, Waterloo.

---

## Role Data

### Backend

**High-bar signals:**
- Staff/Principal/Distinguished titles
- Systems design content (blogs, talks)
- Open source contributions to infra/databases/compilers
- Ex: Stripe, Cloudflare, Databricks, Cockroach Labs, PlanetScale
- Mentions: distributed systems, Rust, Go, high throughput, latency
- 🚀 Startup-ready: Founding or early engineer (#1–5) anywhere
- Shipped backend systems solo — no platform team, no SRE safety net
- Side projects or OSS tooling with real GitHub traction
- Career arc shows increasing scope, not just title inflation
- Comfortable being on-call for everything they build

**Niche sourcing channels:**
- **GitHub:** Search contributors to repos: cockroachdb, tikv, neon, turso, drizzle-orm. Stars on systems repos = signal. [Link](https://github.com/search?q=stars%3A%3E100+language%3ARust+language%3AGo&type=repositories)
- **LinkedIn X-Ray:** `site:linkedin.com/in "Staff Engineer" OR "Principal Engineer" "distributed systems" ("Stripe" OR "Cloudflare" OR "Databricks") -recruiter`
- **Substack / Blog:** Search 'distributed systems' or 'building X at scale' on Substack. Engineers who write = high agency, communicative. [Link](https://substack.com/search/distributed%20systems)
- **HackerNews:** hn.algolia.com — search for engineers commenting on systems topics. Profile → find their LinkedIn. [Link](https://hn.algolia.com)

**Boolean strings:**
1. LI Recruiter — Senior Backend (systems + top schools): `("backend engineer" OR "software engineer" OR "SWE") AND ("distributed systems" OR "high throughput" OR "low latency" OR "Rust" OR "Go" OR "Postgres") AND ("Stripe" OR "Cloudflare" OR "Databricks" OR "Cockroach Labs" OR "PlanetScale" OR "Neon" OR "Temporal" OR "Figma" OR "Rippling" OR "Brex" OR "Plaid" OR "Notion" OR "Retool" OR "Vercel" OR "Scale AI" OR "Anduril") AND ("Staff" OR "Senior" OR "Principal") NOT "recruiting" NOT "looking"`
2. LI Recruiter — Top school backend (CS pedigree signal): `("software engineer" OR "backend engineer" OR "SWE") AND ("distributed systems" OR "Rust" OR "Go" OR "systems design") AND ("MIT" OR "Stanford" OR "Carnegie Mellon" OR "UC Berkeley" OR "UIUC" OR "Georgia Tech" OR "Cornell" OR "University of Washington" OR "Princeton" OR "Caltech" OR "UT Austin" OR "Purdue" OR "Michigan") NOT "recruiter" NOT "looking"`
3. Google X-Ray — Backend (combined school + company signal): `site:linkedin.com/in ("backend" OR "software engineer") ("Rust" OR "Go" OR "distributed") ("Stripe" OR "Databricks" OR "Cloudflare" OR "Temporal" OR "Neon") ("MIT" OR "Stanford" OR "CMU" OR "Berkeley" OR "UIUC" OR "Georgia Tech" OR "Cornell") -recruiter`

**Outreach tips:**
1. Lead with a specific technical detail from their profile or GitHub — shows you read it.
2. Name the hard problem they'd be working on, not the company name first.
3. Reference their tech stack directly: 'Given your work in Go and distributed consensus...'
4. Keep it under 4 sentences. High-bar engineers delete long messages.
5. If they have a blog/OSS work, cite it: 'I read your post on X — that's exactly the kind of thinking [Company] needs.'

---

### Frontend

**High-bar signals:**
- Contributes to or authors popular UI libraries
- Portfolio with shipped consumer products
- Mentions: performance, accessibility, design systems, Core Web Vitals
- Ex: Vercel, Linear, Figma, Notion, Loom
- 🚀 Startup-ready: Personal portfolio site with clean, opinionated design choices
- Side projects shipped to real users — not just localhost

**Niche sourcing channels:**
- **Twitter/X:** Search 'CSS' OR 'React performance' OR 'design system'. Frontend eng Twitter is very active. [Link](https://twitter.com/search?q=design+system+shipped&f=people)
- **GitHub:** Contributors to: shadcn/ui, Radix, Framer Motion, React Query, Next.js. These are high-bar frontend engineers. [Link](https://github.com/shadcn-ui/ui/graphs/contributors)
- **LinkedIn X-Ray:** `site:linkedin.com/in ("frontend engineer" OR "UI engineer") ("design system" OR "React" OR "performance") ("Figma" OR "Linear" OR "Vercel" OR "Notion") -recruiter`

**Boolean strings:**
1. LI Recruiter — Senior Frontend (craft + top companies): `("frontend engineer" OR "UI engineer" OR "software engineer") AND ("React" OR "TypeScript" OR "design system" OR "performance" OR "accessibility") AND ("Linear" OR "Vercel" OR "Raycast" OR "Framer" OR "Figma" OR "Notion" OR "Loom" OR "Stripe" OR "Superhuman" OR "Arc" OR "Webflow" OR "Clerk" OR "Supabase" OR "Retool" OR "Pitch") AND ("Staff" OR "Senior") NOT "recruiter"`
2. LI Recruiter — Frontend (top school + ecosystem): `("frontend engineer" OR "UI engineer" OR "software engineer") AND ("React" OR "TypeScript" OR "Next.js" OR "Web Components") AND ("MIT" OR "Stanford" OR "Carnegie Mellon" OR "UC Berkeley" OR "Cornell" OR "UIUC" OR "Michigan" OR "UCLA" OR "Georgia Tech" OR "USC" OR "NYU" OR "Northeastern") NOT "recruiter"`

**Outreach tips:**
1. Reference something they've shipped — a product, a component, a tweet about a problem they solved.
2. Frontend engineers care about design quality. Mention if the company has strong design culture.
3. Performance and craft matter to the best ones — mention if they'll own the design system.

---

### Fullstack

**High-bar signals:**
- Shipped consumer products end-to-end
- Can speak to both DB schema design and UI architecture
- Ex: early-stage startups where they owned the stack
- Mentions: Next.js, tRPC, Postgres, TypeScript
- 🚀 Startup-ready: 'I was the only engineer for the first year' energy
- Side projects with real traction (paying users, GitHub stars, Product Hunt launches)

**Niche sourcing channels:**
- **LinkedIn (Founding Eng filter):** Search 'founding engineer' or 'engineer #1' — these people have done everything.
- **YC Alumni Network:** Find engineers who worked at YC companies in their early days. [Link](https://www.ycombinator.com/companies)
- **GitHub:** Contributors to Next.js, tRPC, Prisma, Supabase. Full-stack framework contributors are strong signal. [Link](https://github.com/vercel/next.js/graphs/contributors)

**Boolean strings:**
1. LI Recruiter — Founding / Early Eng (top companies): `("founding engineer" OR "software engineer" OR "full stack") AND ("TypeScript" OR "React" OR "Next.js" OR "Node" OR "Postgres" OR "tRPC") AND ("Retool" OR "Coda" OR "Supabase" OR "Glide" OR "Notion" OR "Linear" OR "Vercel" OR "Airtable" OR "Webflow" OR "Clerk" OR "Railway" OR "Loom" OR "Pitch") NOT "recruiter"`
2. LI Recruiter — Fullstack (top CS schools + stack): `("full stack" OR "fullstack" OR "software engineer") AND ("Next.js" OR "TypeScript" OR "React" OR "tRPC" OR "Postgres") AND ("MIT" OR "Stanford" OR "Carnegie Mellon" OR "UC Berkeley" OR "Cornell" OR "UIUC" OR "Georgia Tech" OR "Michigan" OR "UCLA" OR "USC" OR "NYU" OR "Northeastern") NOT "recruiter"`

**Outreach tips:**
1. Emphasize ownership — they'll own features end-to-end, not just a slice of the stack.
2. Mention team size and their scope: 'You'd be engineer #4, working directly with the founders.'
3. Speed of shipping is a real sell: 'They ship weekly, no committee, just build.'

---

### Infrastructure / DevOps

**High-bar signals:**
- Staff/Principal SRE or Platform Engineer titles
- Kubernetes, Terraform, large-scale incident response experience
- Contributions to CNCF projects
- Ex: Cloudflare, Datadog, HashiCorp, PagerDuty, Fastly
- 🚀 Startup-ready: Built entire infra stack from scratch at a sub-50-person company
- Comfortable being the only infra person — no platform team, no SRE org

**Niche sourcing channels:**
- **GitHub / CNCF:** Browse contributors to Kubernetes, Prometheus, Terraform, ArgoCD. Active contributors = senior practitioners. [Link](https://github.com/kubernetes/kubernetes/graphs/contributors)
- **KubeCon / Conference Speakers:** KubeCon speaker list is a goldmine. Find the talk, find the speaker, find their LinkedIn. [Link](https://events.linuxfoundation.org/kubecon-cloudnativecon-north-america/)
- **LinkedIn X-Ray:** `site:linkedin.com/in ("site reliability" OR "platform engineer" OR "DevOps") ("Kubernetes" OR "Terraform") ("Staff" OR "Principal" OR "Senior") -recruiter`

**Boolean strings:**
1. LI Recruiter — Staff SRE / Platform Eng (top companies): `("site reliability engineer" OR "platform engineer" OR "infrastructure engineer") AND ("Kubernetes" OR "Terraform" OR "multi-region" OR "CI/CD" OR "ArgoCD") AND ("Cloudflare" OR "Datadog" OR "HashiCorp" OR "Fastly" OR "Fly.io" OR "Render" OR "Stripe" OR "Figma" OR "Rippling" OR "Cockroach Labs" OR "Temporal" OR "Railway" OR "Neon" OR "Vercel") AND ("Staff" OR "Principal" OR "Senior") NOT "recruiter"`
2. LI Recruiter — Infra (top CS schools): `("infrastructure" OR "SRE" OR "platform engineer" OR "DevOps") AND ("Kubernetes" OR "Terraform" OR "AWS" OR "GCP" OR "distributed systems") AND ("MIT" OR "Stanford" OR "Carnegie Mellon" OR "UC Berkeley" OR "UIUC" OR "Georgia Tech" OR "Cornell" OR "University of Washington" OR "Purdue" OR "Michigan" OR "UT Austin" OR "Virginia Tech") NOT "recruiter"`

**Outreach tips:**
1. Mention scale explicitly: 'They're running X requests/sec across Y regions and the platform team owns the whole thing.'
2. Infra engineers care about on-call load — if the company has a healthy on-call culture, say so.
3. Autonomy over tooling choices is a big draw. Mention if greenfield.
4. These candidates are often skeptical of startups. Name the infra challenge specifically.

---

### ML Engineer

**High-bar signals:**
- Published papers (NeurIPS, ICML, ICLR, ACL)
- Kaggle Grandmaster or top-tier competition wins
- PhD or research lab experience (FAIR, Google Brain, DeepMind, MSR)
- Open source ML frameworks contributions (HuggingFace, PyTorch)
- Mentions: training at scale, RLHF, fine-tuning, inference optimization
- 🚀 Startup-ready: Left academia or top research lab to join a startup
- Owns the full ML lifecycle: data, training, serving, monitoring
- Side projects: HuggingFace repos, personal model releases, open-source ML tooling

**Niche sourcing channels:**
- **Semantic Scholar / ArXiv:** Find authors on relevant papers. Search their name on LinkedIn. Grad students about to graduate = high potential passive candidates. [Link](https://arxiv.org/search/?searchtype=all&query=reinforcement+learning+language+models)
- **HuggingFace:** Browse top model contributors. Click profiles → find GitHub → find LinkedIn. [Link](https://huggingface.co/models?sort=downloads)
- **Kaggle:** Filter Grandmasters and Masters. Many list LinkedIn in their profile. Strong signal for applied ML ability. [Link](https://www.kaggle.com/rankings)
- **LinkedIn X-Ray:** `site:linkedin.com/in ("machine learning" OR "ML engineer") ("NeurIPS" OR "ICML" OR "PhD" OR "research scientist") -recruiter`

**Boolean strings:**
1. LI Recruiter — Research-adjacent ML (top programs): `("machine learning engineer" OR "research engineer" OR "ML engineer") AND ("NeurIPS" OR "ICML" OR "ICLR" OR "PhD" OR "research scientist") AND ("MIT" OR "Stanford" OR "Carnegie Mellon" OR "UC Berkeley" OR "University of Washington" OR "Cornell" OR "Princeton" OR "Caltech" OR "UIUC" OR "Georgia Tech") NOT "recruiter"`
2. LI Recruiter — Applied ML (production + top companies): `("machine learning" OR "ML engineer") AND ("production" OR "inference" OR "fine-tuning" OR "RLHF" OR "training at scale" OR "PyTorch" OR "JAX") AND ("Anthropic" OR "OpenAI" OR "Cohere" OR "Mistral" OR "Together AI" OR "Modal" OR "Replicate" OR "Runway" OR "Scale AI" OR "Hugging Face" OR "DeepMind" OR "Google Brain" OR "Meta AI") AND ("Staff" OR "Senior" OR "Lead") NOT "recruiter"`
3. Google X-Ray — ML (school + lab + company): `site:linkedin.com/in ("machine learning" OR "ML") ("NeurIPS" OR "ICML" OR "PyTorch" OR "RLHF") ("Anthropic" OR "OpenAI" OR "Google Brain" OR "FAIR" OR "Cohere" OR "Mistral") ("MIT" OR "Stanford" OR "CMU" OR "Berkeley" OR "UW" OR "Cornell") -recruiter`

**Outreach tips:**
1. Reference their paper or model by name if they have one.
2. Mention the research direction of the team, not just 'AI startup'.
3. Be honest about compute resources and data access.
4. If they're academic, acknowledge the transition: 'A lot of folks from [Lab] have found that [Company] gives them the compute and freedom they couldn't get in academia.'
5. Don't pitch equity first. Lead with the problem.

---

### AI Engineer

**High-bar signals:**
- Building with LLM APIs (OpenAI, Anthropic, Cohere)
- Mentions: agents, RAG, evals, prompt engineering, function calling
- Active on Twitter/X AI community
- OSS tools: LangChain, LlamaIndex, DSPy contributors
- 🚀 Startup-ready: Ships AI demos and side projects publicly (Twitter, GitHub, HuggingFace)
- Won AI hackathons or shipped a viral AI-powered tool
- Self-taught with no formal ML background but demonstrated ability to ship

**Niche sourcing channels:**
- **Twitter / X:** Search 'building with Claude' OR 'LLM in production' OR 'RAG pipeline'. Engineers sharing work = open to conversations. [Link](https://twitter.com/search?q=building%20with%20Claude%20OR%20%22LLM%20in%20production%22&f=people)
- **GitHub:** Contributors to LangChain, LlamaIndex, DSPy, instructor, outlines. Fork counts + recent commits = active builders. [Link](https://github.com/langchain-ai/langchain/graphs/contributors)
- **LinkedIn X-Ray:** `site:linkedin.com/in ("AI engineer" OR "LLM" OR "generative AI") ("agents" OR "RAG" OR "evals") -recruiter -"looking"`
- **Buildspace / Hackathons:** Devpost, Lablab.ai, and AI hackathon winners. These people build fast and ship things. [Link](https://lablab.ai/event)

**Boolean strings:**
1. LI Recruiter — AI Engineer (applied + top companies): `("AI engineer" OR "LLM engineer" OR "software engineer") AND ("agents" OR "RAG" OR "evals" OR "fine-tuning" OR "LLM" OR "prompt") AND ("Cursor" OR "Perplexity" OR "LangChain" OR "Vellum" OR "Braintrust" OR "Anthropic" OR "OpenAI" OR "Cohere" OR "Glean" OR "Harvey" OR "Hebbia" OR "Writer" OR "Cognition" OR "Replit") NOT "recruiter"`
2. LI Recruiter — SWE transitioning to AI (school signal): `("software engineer" OR "backend engineer") AND ("OpenAI" OR "Anthropic" OR "LangChain" OR "LlamaIndex" OR "Claude" OR "GPT" OR "agents" OR "RAG") AND ("MIT" OR "Stanford" OR "Carnegie Mellon" OR "UC Berkeley" OR "UIUC" OR "Georgia Tech" OR "Cornell" OR "University of Washington" OR "Princeton" OR "Caltech" OR "Northeastern" OR "NYU") NOT "recruiter"`
3. Google X-Ray — AI Engineer (school + company): `site:linkedin.com/in ("AI engineer" OR "LLM") ("agents" OR "RAG" OR "evals") ("Anthropic" OR "OpenAI" OR "Cursor" OR "Perplexity" OR "Cohere") ("MIT" OR "Stanford" OR "CMU" OR "Berkeley" OR "UIUC" OR "Georgia Tech") -recruiter`

**Outreach tips:**
1. Name a specific OSS project or tweet if they have one.
2. Be specific about the stack: 'They're using Claude + custom evals + a TypeScript agent framework.'
3. These candidates move fast — shorter time-to-offer matters.
4. They care about autonomy over AI decisions (model choice, infra). Mention if that's true.

---

### Data Engineer

**High-bar signals:**
- Mentions: dbt, Airflow, Spark, Snowflake, data modeling, pipelines at scale
- Ex: Databricks, dbt Labs, Snowflake, Fivetran, Monte Carlo
- 🚀 Startup-ready: 'I built the data warehouse from scratch' — zero-to-one experience
- Was the sole data engineer at a startup, owned the whole stack
- Active in dbt Slack or data communities

**Niche sourcing channels:**
- **dbt Community Slack:** dbt Slack has 50k+ members. Find active contributors in #show-and-tell and #general. [Link](https://www.getdbt.com/community/join-the-community)
- **LinkedIn X-Ray:** `site:linkedin.com/in ("data engineer" OR "analytics engineer") ("dbt" OR "Airflow" OR "Spark" OR "Snowflake") ("Staff" OR "Senior" OR "Lead") -recruiter`
- **GitHub:** Contributors to dbt-core, Apache Airflow, Great Expectations. [Link](https://github.com/dbt-labs/dbt-core/graphs/contributors)

**Boolean strings:**
1. LI Recruiter — Senior Data Eng (top companies): `("data engineer" OR "analytics engineer" OR "data platform engineer") AND ("dbt" OR "Airflow" OR "Spark" OR "Snowflake" OR "Kafka" OR "Databricks") AND ("dbt Labs" OR "Fivetran" OR "Monte Carlo" OR "Hightouch" OR "Databricks" OR "Snowflake" OR "Astronomer" OR "Hex" OR "Airbyte" OR "Segment" OR "Amplitude" OR "Stripe" OR "Brex") AND ("Staff" OR "Senior" OR "Lead") NOT "recruiter"`
2. LI Recruiter — Data Eng (top CS schools + tools): `("data engineer" OR "analytics engineer") AND ("dbt" OR "Airflow" OR "Spark" OR "Snowflake" OR "Kafka") AND ("MIT" OR "Stanford" OR "Carnegie Mellon" OR "UC Berkeley" OR "UIUC" OR "Georgia Tech" OR "Michigan" OR "Cornell" OR "UT Austin" OR "UMass Amherst" OR "University of Washington") NOT "recruiter"`

**Outreach tips:**
1. Be specific about data scale: rows/day, number of models, pipeline complexity.
2. Data engineers care about tooling choices — mention if they get to pick the stack.
3. If the company is early-stage data, that's a draw: 'You'd be building the data foundation from scratch.'

---

### Forward Deployed Engineer

**High-bar signals:**
- Titles: Forward Deployed Engineer, Solutions Engineer, Field Engineer, Implementation Engineer, Customer Engineer
- Palantir, Anduril, Scale AI, or similar embedded-engineer backgrounds
- Mentions: customer deployment, enterprise rollout, integration work, field work
- Comfort with ambiguity — no spec, no handoff, just a customer problem to solve
- 🚀 Startup-ready: Was the only technical person in a customer engagement
- Can write production code AND sit across from a skeptical enterprise buyer

**Niche sourcing channels:**
- **Palantir Alumni Network:** Palantir FDEs are the gold standard. Search 'Forward Deployed Engineer Palantir' on LinkedIn. Lateral moves from Palantir = very high signal.
- **LinkedIn X-Ray:** `site:linkedin.com/in ("forward deployed" OR "solutions engineer" OR "field engineer") ("enterprise" OR "customer" OR "deployment") ("Palantir" OR "Anduril" OR "Scale AI" OR "Databricks" OR "Datadog") -recruiter`

**Boolean strings:**
1. LI Recruiter — FDE (Palantir / defense tech pipeline): `("forward deployed engineer" OR "field engineer" OR "implementation engineer") AND ("customer" OR "deployment" OR "enterprise" OR "onsite") AND ("Palantir" OR "Anduril" OR "Scale AI" OR "Rebellion Defense" OR "Shield AI" OR "Vannevar Labs") NOT "recruiter"`
2. LI Recruiter — Solutions Eng → FDE (hypergrowth pipeline): `("solutions engineer" OR "customer engineer" OR "field engineer") AND ("integration" OR "implementation" OR "enterprise" OR "API" OR "deployment") AND ("Stripe" OR "Databricks" OR "Snowflake" OR "Datadog" OR "MongoDB" OR "Cockroach Labs" OR "Temporal" OR "Glean" OR "Retool" OR "Hex") AND ("Staff" OR "Senior" OR "Lead") NOT "recruiter"`

**Outreach tips:**
1. Lead with the customer problem, not the product: 'You'd be embedded with enterprise customers solving [specific hard problem].'
2. FDEs care about autonomy and trust — mention that they'll have real latitude to make technical decisions in the field.
3. These candidates want to know they'll still write real code — not become a salesperson. Reassure them.

---

### Product Manager

**High-bar signals:**
- Shipped 0-to-1 products or major features
- Technical background or eng-adjacent experience
- Mentions: discovery, metrics, roadmap, cross-functional
- Ex: Stripe, Linear, Figma, Notion, Loom
- 🚀 Startup-ready: 'I was the first PM hired' — built process from nothing
- Can write specs, pull their own data, and talk to customers in the same week

**Niche sourcing channels:**
- **Lenny's Newsletter community:** Lenny's Slack has thousands of PMs. Active members = engaged, growth-minded PMs who may be open to moves. [Link](https://www.lennysnewsletter.com/about)
- **Twitter/X:** Search product thinking threads, teardowns, or 'what I learned building X'. Writing PMs are high signal. [Link](https://twitter.com/search?q=product+teardown&f=people)
- **LinkedIn X-Ray:** `site:linkedin.com/in ("product manager" OR "PM") ("0 to 1" OR "launched" OR "shipped") ("Stripe" OR "Linear" OR "Figma" OR "Notion") -recruiter`

**Boolean strings:**
1. LI Recruiter — Technical PM (top companies): `("product manager" OR "PM") AND ("technical" OR "API" OR "developer tools" OR "0 to 1") AND ("Linear" OR "Rippling" OR "Deel" OR "Notion" OR "Retool" OR "Brex" OR "Hex" OR "Loom" OR "Coda" OR "Figma" OR "Stripe" OR "Airtable" OR "Amplitude" OR "Superhuman" OR "Carta" OR "Ramp" OR "Mercury") NOT "recruiter"`
2. LI Recruiter — PM (top MBA + undergrad programs): `("product manager" OR "PM" OR "product lead") AND ("roadmap" OR "launched" OR "shipped" OR "PLG" OR "growth") AND ("MIT" OR "Stanford" OR "Harvard" OR "Wharton" OR "Carnegie Mellon" OR "UC Berkeley" OR "Columbia" OR "Kellogg" OR "Booth" OR "Cornell" OR "Duke" OR "Northwestern" OR "Michigan Ross") NOT "recruiter"`

**Outreach tips:**
1. Name the product domain specifically — consumer, B2B SaaS, API/developer tools.
2. PMs care about autonomy and proximity to engineering. Mention if they'll work directly with founders.
3. Avoid generic startup pitches — PMs have heard them all. Lead with the specific problem the product solves.

---

### Product Designer

**High-bar signals:**
- Portfolio with shipped consumer or B2B products
- Mentioned design systems, motion, interaction design
- Ex: Linear, Figma, Notion, Stripe, Vercel (design-forward companies)
- Active on Dribbble, Twitter/X design community, or Layers.to
- 🚀 Startup-ready: 'I was the only designer' — built the design language from scratch

**Niche sourcing channels:**
- **Layers.to:** Layers.to is where top product designers share work. Browse by company or style to find strong candidates. [Link](https://layers.to)
- **Read.cv:** Read.cv is used heavily by designers and design-adjacent engineers. Better signal than LinkedIn for this role. [Link](https://read.cv/explore)
- **LinkedIn X-Ray:** `site:linkedin.com/in ("product designer" OR "UX designer") ("design system" OR "interaction" OR "motion") ("Linear" OR "Figma" OR "Notion" OR "Stripe") -recruiter`

**Boolean strings:**
1. LI Recruiter — Senior Designer (top companies): `("product designer" OR "UX designer") AND ("design system" OR "interaction design" OR "motion" OR "0 to 1") AND ("Linear" OR "Raycast" OR "Framer" OR "Arc" OR "Superhuman" OR "Loom" OR "Vercel" OR "Figma" OR "Notion" OR "Stripe" OR "Pitch" OR "Miro" OR "Webflow" OR "Retool" OR "Mercury" OR "Ramp" OR "Brex") AND ("Staff" OR "Senior" OR "Lead") NOT "recruiter"`
2. LI Recruiter — Designer (top design + CS programs): `("product designer" OR "UX designer" OR "UI designer") AND ("design system" OR "interaction" OR "shipped") AND ("Rhode Island School of Design" OR "RISD" OR "Parsons" OR "Carnegie Mellon" OR "Stanford" OR "MIT" OR "SCAD" OR "ArtCenter" OR "SVA" OR "Pratt" OR "Cornell" OR "Michigan" OR "UC San Diego") NOT "recruiter"`

**Outreach tips:**
1. Reference something specific from their portfolio — a decision they made, not just that it looks good.
2. Designers care about design culture more than any other role. Mention engineer-design collaboration quality.
3. Read.cv or personal site > LinkedIn for designers. If they have one, reference it.

---

## VC-Backed Target Companies

### Backend
*Why:* These companies are known for high-bar backend engineering cultures — distributed systems, high throughput, and strong infra ownership.
- **Neon** — a16z, Series B. Postgres-compatible serverless DB — backend engineers own deep infra.
- **PlanetScale** — a16z, Series C. MySQL-compatible, vitess-based — world-class DB engineering.
- **Turso** — Accel, Seed. Edge SQLite — small team, strong systems engineers.
- **Sequin** — YC, Seed. Postgres change-data-capture — niche but high-signal infra play.
- **Railway** — YC, Series A. Developer infra platform — backend engineers who care about DX.
- **Crunchy Data** — General Catalyst, Series C. Managed Postgres — deep database engineering.
- **Temporal** — Sequoia, Series B. Workflow orchestration — engineers who understand durable execution deeply.
- **Buf** — Sequoia, Series B. Protobuf tooling — API infra, strong Go engineers.
- **Zed Industries** — a16z, Series A. High-perf code editor in Rust — top-tier systems engineers.

Boolean: `("software engineer" OR "backend engineer" OR "SWE") AND ("distributed systems" OR "Rust" OR "Go" OR "Postgres" OR "high throughput" OR "low latency") AND ("Stripe" OR "Cloudflare" OR "Databricks" OR "Cockroach Labs" OR "PlanetScale" OR "Neon" OR "Temporal" OR "Buf" OR "Railway" OR "Figma" OR "Rippling" OR "Brex" OR "Plaid" OR "Notion" OR "Retool" OR "Vercel" OR "Scale AI" OR "Anduril") AND ("Staff" OR "Senior" OR "Principal") NOT "recruiter"`

### Frontend
*Why:* World-class frontend culture — design systems, performance obsession, engineers who blur the line between design and engineering.
- **Linear** — Sequoia, Series B. Arguably the best product design/eng culture today.
- **Vercel** — GV / Accel, Series D. Home of Next.js — frontend engineers at the edge of the ecosystem.
- **Raycast** — Accel, Series A. Craft-obsessed, native+web — elite frontend/product engineers.
- **Framer** — Accel, Series B. No-code/design tool — frontend engineers who understand design deeply.
- **Clerk** — Madrona / YC, Series B. Auth infra with a premium DX — frontend-heavy team, high craft bar.
- **Supabase** — Lightspeed, Series C. Open source Firebase — strong full-stack and frontend engineers.
- **Resend** — YC, Seed. Email infra with elite DX — small team, very high frontend bar.

### Fullstack
*Why:* Small, high-ownership engineering teams where full-stack engineers build entire product surfaces.
- **Retool** — Sequoia / a16z, Series C. Internal tools platform — engineers own the whole product surface.
- **Coda** — Greylock / General Catalyst, Series D. Docs + logic platform — full-stack with strong product thinking.
- **Glide** — General Catalyst, Series B. No-code app builder — small team, full-stack ownership.
- **Supabase** — Lightspeed, Series C. Open-source Firebase alternative — fullstack engineers who ship OSS.
- **Interval** — YC / Sequoia, Seed. Internal tooling infra — strong founding-era engineers.

### Infrastructure / DevOps
*Why:* Infra at their core — engineers here own multi-region systems, reliability, and platform architecture.
- **Fly.io** — a16z, Series B. Edge compute platform — infra engineers who understand distributed deployment deeply.
- **Render** — General Catalyst, Series B. Cloud hosting platform — platform engineers with full-stack infra ownership.
- **Depot** — Lightspeed, Series A. Fast Docker builds — CI/CD infra engineers.
- **Dagger** — a16z, Series B. Portable CI/CD engine — DevOps tooling engineers with deep Docker/Buildkit knowledge.
- **Warp** — Figma / GV, Series B. Terminal reimagined — systems engineers who care deeply about developer tooling.

### ML Engineer
*Why:* Frontier of applied ML — training at scale, RLHF, inference optimization.
- **Cohere** — General Catalyst / Nvidia, Series C. Enterprise LLMs.
- **Mistral AI** — Lightspeed / a16z, Series B. Open-weight frontier models — research-grade ML engineers.
- **Together AI** — Salesforce Ventures / a16z, Series A. Distributed training and inference — deep ML infra.
- **Modal** — Redpoint, Series B. Cloud for ML workloads — engineers who understand GPU infra and ML pipelines.
- **Replicate** — a16z, Series B. Model hosting platform — ML engineers who ship models to production.
- **Runway** — General Catalyst / Sequoia, Series C. Generative video — multimodal ML engineers.

### AI Engineer
*Why:* AI-native products — agents, RAG pipelines, evals, and LLM-powered workflows.
- **Cursor** — a16z / Thrive, Series B. AI code editor — deeply integrated LLM UX.
- **Perplexity** — Nvidia / NEA, Series B. AI search — RAG and retrieval at scale.
- **Langchain** — Benchmark, Series A. LLM orchestration framework.
- **Vellum** — YC, Series A. LLM prompt/eval management.
- **Braintrust** — YC / Lightspeed, Series A. AI eval platform.
- **Elicit** — Accel, Series A. AI research assistant — LLM engineers with research domain depth.

### Data Engineer
*Why:* Data at their core — pipelines, platforms, and tooling that power modern data stacks.
- **dbt Labs** — Sequoia / Andreessen, Series D. Defines modern data transformation.
- **Fivetran** — General Catalyst, Series D. Data integration leader.
- **Monte Carlo** — Accel / GV, Series C. Data observability.
- **Hightouch** — a16z / Bain Capital Ventures, Series B. Reverse ETL — data activation engineers.
- **Cube** — Eniac / Bain, Series B. Semantic layer — data engineers who think about modeling and metrics.

### Forward Deployed Engineer
*Why:* World-class FDE cultures — engineers at the intersection of software, customer empathy, and rapid problem-solving.
- **Palantir** — Public. Invented the FDE archetype.
- **Anduril** — Founders Fund / a16z, Series F. Defense tech with embedded engineers in the field.
- **Scale AI** — Accel / Tiger Global, Series F. Data infrastructure with embedded customer solutions engineers.
- **Glean** — Sequoia / Lightspeed, Series D. Enterprise AI search — FDEs help customers deploy and extract value.
- **Retool** — Sequoia / a16z, Series C. Internal tools — solutions engineers who can build and advise simultaneously.
- **Temporal** — Sequoia, Series B. Workflow orchestration — engineers who help customers implement complex patterns.
- **Stripe** — Sequoia / General Catalyst, Public. Payments infra — customer-facing API integration at scale.

### Product Manager
*Why:* High-bar PM cultures — strong discovery, metrics-driven roadmaps, and tight eng-PM collaboration.
- **Linear** — Sequoia, Series B. Legendary product culture.
- **Rippling** — Sequoia / Founders Fund, Series F. Compound startup — PMs managing complex multi-product surfaces.
- **Notion** — Sequoia / Index, Series C. PLG excellence — bottoms-up growth.
- **Retool** — Sequoia / a16z, Series C. Developer tools PM — technically fluent PMs.
- **Brex** — Greenoaks / Ribbit, Series D. Fintech infra — PMs with financial product and compliance depth.

### Product Designer
*Why:* Craft-obsessed design cultures where designers have real ownership.
- **Linear** — Sequoia, Series B. The gold standard for product design in tech.
- **Raycast** — Accel, Series A. Pixel-perfect, interaction-heavy.
- **Framer** — Accel, Series B. Design-to-code tool.
- **Arc Browser** — General Catalyst, Series B. Reinvented the browser — bold, opinionated product designers.
- **Superhuman** — Andreessen / FirstRound, Series B. Speed + delight — designers obsessed with reducing friction.

---

## Email Drip Generation

**System prompt for generic outreach:**
```
You are an expert technical recruiter at SingleSprout. Write warm, punchy, human outreach to passive candidates. Tone: friendly, direct — like a smart colleague, not a cold sales rep.
Rules: "Hey" not "Hi", 4–5 sentences max, never "rockstar/ninja/guru/superstar/passionate/disruptive/our team would love to chat", no salary/comp, sign off [Your Name].
Output valid JSON only: {"email1":{"subject":"...","body":"..."},"email2":{"subject":"...","body":"..."},"email3":{"subject":"...","body":"..."},"email4":{"subject":"...","body":"..."},"inmail":{"subject":"...","body":"..."}}
```

**For generic (no specific company):** Emphasize SingleSprout's access to 80+ VC-backed companies. Use {firstName} as placeholder.

**For specific role:** Name the company, funding, mission. Make the candidate curious. Email 4 is a soft close. InMail is tighter/shorter.
