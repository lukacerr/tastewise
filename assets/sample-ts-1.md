tastewise on  main [?] is 📦 v1.0.0 via 🐍 v3.14.4 (tastewise)
❯ uv run main.py '/home/luka/Documents/tastewise/transcripts/ts-1.txt'
19:28:06 INFO Starting transcript agent: threshold=0.60
19:28:06 INFO Reading transcript: /home/luka/Documents/tastewise/transcripts/ts-1.txt
19:28:06 INFO Transcript loaded: 995 characters
19:28:06 INFO Evaluating whether to abstain
19:28:06 INFO Invoking abstain agent
19:28:13 INFO HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
19:28:13 INFO Abstain agent finished: transcript_value=0.85 confidence=0.90
19:28:13 INFO Abstain decision: value_index=0.77 threshold=0.60 abstained=False
19:28:13 INFO Routing after abstain evaluation: extract_updates
19:28:13 INFO Extracting opportunity updates
19:28:13 INFO Invoking extraction agent
19:28:33 INFO HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
19:28:33 INFO Extraction agent finished: stage=discovery->proposal risks=1
19:28:33 INFO Summarizing last touch
19:28:33 INFO Invoking summary agent
19:28:36 INFO HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
19:28:36 INFO Summary agent finished
19:28:36 INFO Routing after summary: create_opportunity
19:28:36 INFO Creating final opportunity payload
19:28:36 INFO Opportunity payload created: stage=proposal average_confidence=0.84
19:28:36 INFO Transcript agent finished
```json
{
  "deal_stage_delta": {
    "value": [
      "discovery",
      "proposal"
    ],
    "confidence_score": 0.75,
    "justification": "The conversation references prior discovery, discusses evaluation criteria, pricing, and a revised quote being sent, suggesting a move from discovery/",
    "timestamp_quotes": [
      "[00:18] Priya: Yeah — Ben's in the next call. He's fine with the $120k range but wants annual not quarterly.",
      "[02:05] AE: Okay. So on my side — I'll send a revised quote tonight annual, and a one-pager on stage-gate integration by Friday."
    ]
  },
  "amount_usd": {
    "value": 120000.0,
    "confidence_score": 0.95,
    "justification": "Priya explicitly states Ben is fine with the $120k range.",
    "timestamp_quotes": [
      "[00:18] Priya: Yeah — Ben's in the next call. He's fine with the $120k range but wants annual not quarterly."
    ]
  },
  "close_date": {
    "value": "2026-10-01",
    "confidence_score": 0.7,
    "justification": "Priya says pushing to early Q4 now. Assuming Q4 of the current fiscal year; normalized to 2026-10-01 as first day of Q4.",
    "timestamp_quotes": [
      "[01:30] Priya: Actually pushing to early Q4 now. Our 2027 portfolio review moved."
    ]
  },
  "risks": [
    {
      "value": "Spoonshot competitor with aggressive pricing could undercut the deal",
      "confidence_score": 0.85,
      "justification": "Priya explicitly raises Spoonshot as a competitive concern with aggressive pricing.",
      "timestamp_quotes": [
        "[02:55] Priya: One. I saw Spoonshot in market last week. The demo was lightweight but the price was aggressive. You'll need to be ready for that."
      ]
    }
  ],
  "next_step_description": {
    "value": "AE sends revised annual quote and one-pager on stage-gate integration; Priya loops in Ben and CMO for next call on Tuesday",
    "confidence_score": 0.95,
    "justification": "Both parties commit to specific actions with timing.",
    "timestamp_quotes": [
      "[02:05] AE: Okay. So on my side — I'll send a revised quote tonight annual, and a one-pager on stage-gate integration by Friday. You'll loop in Ben for next Tuesday?",
      "[02:20] Priya: Yes. Ben, me, and our CMO. CMO will be the signer."
    ]
  },
  "next_step_owner": {
    "value": "AE (revised quote & one-pager); Priya (looping in Ben & CMO)",
    "confidence_score": 0.9,
    "justification": "AE commits to sending deliverables; Priya commits to bringing stakeholders.",
    "timestamp_quotes": [
      "[02:05] AE: Okay. So on my side — I'll send a revised quote tonight annual, and a one-pager on stage-gate integration by Friday. You'll loop in Ben for next Tuesday?",
      "[02:20] Priya: Yes. Ben, me, and our CMO."
    ]
  },
  "next_step_due_date": {
    "value": "2026-10-06",
    "confidence_score": 0.6,
    "justification": "Next Tuesday referenced; assuming the Tuesday following the current conversation. Exact date not stated, estimated.",
    "timestamp_quotes": [
      "[02:05] AE: You'll loop in Ben for next Tuesday?",
      "[02:20] Priya: Yes."
    ]
  },
  "metrics": [
    {
      "value": "Speed-to-insight as #1 evaluation criterion",
      "confidence_score": 0.9,
      "justification": "Priya confirms speed is the top criterion.",
      "timestamp_quotes": [
        "[00:45] Priya: Speed is #1."
      ]
    }
  ],
  "economic_buyer": [
    {
      "value": "CMO",
      "confidence_score": 0.9,
      "justification": "Priya states the CMO will be the signer, indicating final purchasing authority.",
      "timestamp_quotes": [
        "[02:20] Priya: Yes. Ben, me, and our CMO. CMO will be the signer."
      ]
    }
  ],
  "decision_criteria": [
    {
      "value": "Speed-to-insight",
      "confidence_score": 0.95,
      "justification": "Priya confirms speed is #1 criterion.",
      "timestamp_quotes": [
        "[00:45] Priya: Speed is #1."
      ]
    },
    {
      "value": "Integration with innovation stage-gate process",
      "confidence_score": 0.9,
      "justification": "Priya states second criterion is how well it integrates with their innovation stage-gate, and wants it in writing.",
      "timestamp_quotes": [
        "[00:45] Priya: Second is how well it integrates with our innovation stage-gate. We'd want that in writing."
      ]
    }
  ],
  "decision_process": [
    {
      "value": "Ben (Procurement) reviews terms; CMO signs off",
      "confidence_score": 0.85,
      "justification": "Priya indicates Ben from Procurement is involved and CMO is the signer.",
      "timestamp_quotes": [
        "[00:18] Priya: Ben's in the next call. He's fine with the $120k range but wants annual not quarterly.",
        "[02:20] Priya: Yes. Ben, me, and our CMO. CMO will be the signer."
      ]
    }
  ],
  "paper_process": [
    {
      "value": "Annual billing structure required by Procurement (Ben)",
      "confidence_score": 0.85,
      "justification": "Ben wants annual not quarterly billing.",
      "timestamp_quotes": [
        "[00:18] Priya: He's fine with the $120k range but wants annual not quarterly."
      ]
    }
  ],
  "identify_pain": [
    {
      "value": "Need for speed-to-insight in portfolio/innovation process",
      "confidence_score": 0.8,
      "justification": "Speed is the #1 criterion, implying current process is slow.",
      "timestamp_quotes": [
        "[00:45] Priya: Speed is #1."
      ]
    },
    {
      "value": "Integration gap with innovation stage-gate process",
      "confidence_score": 0.8,
      "justification": "Second criterion is stage-gate integration, implying current tools don't integrate well.",
      "timestamp_quotes": [
        "[00:45] Priya: Second is how well it integrates with our innovation stage-gate."
      ]
    }
  ],
  "champion": [
    {
      "value": "Priya",
      "confidence_score": 0.85,
      "justification": "Priya is actively driving the deal, looping in stakeholders, and advocating internally.",
      "timestamp_quotes": [
        "[00:18] Priya: Yeah — Ben's in the next call.",
        "[02:20] Priya: Yes. Ben, me, and our CMO."
      ]
    }
  ],
  "competition": [
    {
      "value": "Spoonshot",
      "confidence_score": 0.85,
      "justification": "Priya mentions seeing Spoonshot in market with aggressive pricing.",
      "timestamp_quotes": [
        "[02:55] Priya: I saw Spoonshot in market last week. The demo was lightweight but the price was aggressive."
      ]
    }
  ],
  "detractors": [],
  "opportunity_id": "57f04027-3f2c-4151-a1dc-82a02cdca570",
  "stage": "proposal",
  "average_confidence": 0.8441176470588235,
  "abstainReasoning": {
    "transcript_value": 0.85,
    "confidence": 0.9,
    "justification": "The transcript contains clear actionable CRM signals: a defined deal amount ($120k annual), updated close timeline (early Q4), decision criteria (speed-to-insight, integration with stage‑gate), identified buyer roles (Ben in procurement, CMO as signer), next steps (AE to send revised quote and one‑p"
  },
  "last_touch_summary": "AE will send revised annual quote and stage‑gate integration one‑pager, with Ben, Priya and CMO looping in for next Tuesday; Priya notes competitor Spoonshot's aggressive pricing."
}
```
19:28:36 INFO Printed opportunity result
