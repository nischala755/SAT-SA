# SAT-SA: 2–3 minute narrated demo

Use the live, authenticated **synthetic** deployment. Prepare the `demo` analytics run before recording and keep the identity token private. The Cloudflare Quick Tunnel URL can change when the connector restarts. Record in 1080p, zoom the browser enough for judges to read source references, and avoid displaying the token or `.env.cloudflare.local`.

| Time | Screen action | Narration |
| --- | --- | --- |
| 0:00–0:18 | Show title and Overview. | “NCIIPC supervisors review SOC alerts and cases to judge how cyber-resilience controls operate in practice. SAT-SA helps them decide what requires attention and why. It supports human examination; it does not act as a SOC or make compliance decisions.” |
| 0:18–0:38 | Show the selected `demo` run, CSE table, sector filter, and completeness column. | “This is a periodic, synthetic submission across multiple critical-sector entities. The records are normalized and versioned. The overview shows entities, alerts, cases, review indicators, and data completeness. These counts come from stored evidence, not a mock dashboard.” |
| 0:38–1:03 | Open **Entities**, assess one CSE, then **Inspect evidence** on a fast-closure or escalation indicator. | “Here, an indicator highlights an operational pattern that merits review. Its explanation states what was observed, the rule and threshold used, confidence, and the supporting record count. I can open the source alert or case rather than accepting a score without context.” |
| 1:03–1:27 | Open **Negative space** and inspect a critical-asset monitoring gap. | “SAT-SA also looks for expected evidence that is absent. The asset inventory provides the expectation; the submitted alerts provide the observation. A gap is a supervisory question, not proof of a control failure. If inventory or completeness is inadequate, the analysis says so.” |
| 1:27–1:47 | Show **Review queue** and its reasons/contributions. | “The review queue brings higher-value samples forward and explains each recommendation through severity, recurrence, evidence strength, and data quality. A supervisor still decides which records to examine.” |
| 1:47–2:08 | Open one signal’s source record; in **Human examination**, enter a short synthetic note and choose **further_investigation**. | “After inspecting the underlying record, I record my own examination outcome. The application keeps that human decision separate from analytical indicators and records it in the audit trail.” |
| 2:08–2:26 | Open **Audit trail**, then **Validation**. | “The audit trail ties actions to the examiner and run. Synthetic ground-truth labels are stored separately from normal analytical inputs. Validation reports this synthetic benchmark separately from human-reviewed outcomes; it is not a claim of parity with NCIIPC experts.” |
| 2:26–2:42 | Show **Report**, then return to Overview or the architecture slide. | “Reports retain methods, limitations, and source references. The core system runs locally with FastAPI, Next.js, DuckDB, Parquet, and Docker Compose, without Internet or an external AI model. The public link is only a synthetic demonstration tunnel.” |

Total narration target: **about 2 minutes 40 seconds** at a measured pace. If recording must be under two minutes, use [the shorter script](demo-script.md). Do not show a fabricated finding, claim expert-validated performance, or say the Quick Tunnel is permanently hosted.

## Recording checklist

1. Confirm the public `/api/status` reports `ok: true` and `storage_ready: true`; check **Backend connected** in the page.
2. Sign in using the configured demo identity before recording. On this Windows host, the token can be copied directly to the clipboard without printing it in the terminal:

   ```powershell
   .venv\Scripts\python.exe -c "import json,pathlib; e=dict(x.split('=',1) for x in pathlib.Path('.env.cloudflare.local').read_text().splitlines() if '=' in x and not x.startswith('#')); print(next(iter(json.loads(e['SAT_SA_AUTH_TOKENS']))))" | Set-Clipboard
   ```

3. Select the existing completed `demo` run, or run analytics once before recording. Keep the browser on synthetic records only.
4. Pause briefly on the indicator rationale and source reference so judges can read them. Record the review outcome under an obvious synthetic demonstration note.
5. Verify playback, speech clarity, legible text, and total duration before submission.
