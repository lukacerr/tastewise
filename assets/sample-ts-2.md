tastewise on  main [?] is 📦 v1.0.0 via 🐍 v3.14.4 (tastewise)
❯ uv run main.py '/home/luka/Documents/tastewise/transcripts/ts-2.txt'
19:33:05 INFO Starting transcript agent: threshold=0.60
19:33:05 INFO Reading transcript: /home/luka/Documents/tastewise/transcripts/ts-2.txt
19:33:05 INFO Transcript loaded: 419 characters
19:33:05 INFO Evaluating whether to abstain
19:33:05 INFO Invoking abstain agent
19:33:09 INFO HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
19:33:09 INFO Abstain agent finished: transcript_value=0.20 confidence=0.70
19:33:09 INFO Abstain decision: value_index=0.14 threshold=0.60 abstained=True
19:33:09 INFO Routing after abstain evaluation: summarize_touch
19:33:09 INFO Summarizing last touch
19:33:09 INFO Invoking summary agent
19:33:13 INFO HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
19:33:13 INFO Summary agent finished
19:33:13 INFO Routing after summary: __end__
19:33:13 INFO Transcript agent finished
```json
{
  "abstained": true,
  "transcript_value": 0.2,
  "confidence": 0.7,
  "value_index": 0.13999999999999999,
  "justification": "The transcript provides only a vague timeline (potentially two weeks) and mentions waiting on finance, with no concrete details on amount, stage change, decision criteria, next steps beyond a vague ping, and no buyer roles or risks. This yields low actionable CRM signal, though the timing hint is a\u202f",
  "last_touch_summary": "Champion confirmed they\u2019re still awaiting finance response, expect a decision in about two weeks and will ping AE with an update."
}
```
19:33:13 INFO Printed abstain result
