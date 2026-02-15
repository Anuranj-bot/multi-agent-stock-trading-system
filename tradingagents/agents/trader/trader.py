import functools


def create_trader(llm, memory):

    # -------------------------
    # Utility to trim long text
    # -------------------------
    def trim(text, max_chars=3000):
        if not text:
            return ""
        return text[-max_chars:]  # keep most recent part only

    def trader_node(state, name):

        company_name = state.get("company_of_interest", "")
        investment_plan = trim(state.get("investment_plan", ""), 2500)

        # Trim large research reports
        market_research_report = trim(state.get("market_report", ""), 2000)
        sentiment_report = trim(state.get("sentiment_report", ""), 1500)
        news_report = trim(state.get("news_report", ""), 1500)
        fundamentals_report = trim(state.get("fundamentals_report", ""), 2000)

        # -------------------------
        # Memory handling (safe)
        # -------------------------
        curr_situation = (
            market_research_report
            + "\n\n"
            + sentiment_report
            + "\n\n"
            + news_report
            + "\n\n"
            + fundamentals_report
        )

        past_memory_str = ""

        try:
            past_memories = memory.get_memories(curr_situation, n_matches=1)

            if past_memories and isinstance(past_memories, list):
                for rec in past_memories:
                    if isinstance(rec, dict) and "recommendation" in rec:
                        past_memory_str += trim(rec["recommendation"], 1000) + "\n\n"
        except Exception:
            past_memory_str = ""

        if not past_memory_str:
            past_memory_str = "No significant past lessons available."

        # -------------------------
        # Build compact prompt
        # -------------------------
        messages = [
            {
                "role": "system",
                "content": f"""
You are a professional trading decision agent.

Your task:
- Review the proposed investment plan.
- Consider trimmed research context.
- Learn from past mistakes.
- Make a decisive call: BUY, SELL, or HOLD.

Rules:
- Be concise but strategic.
- Avoid unnecessary repetition.
- End your response with:
FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**

Past Lessons:
{past_memory_str}
""",
            },
            {
                "role": "user",
                "content": f"""
Company: {company_name}

Proposed Investment Plan:
{investment_plan}

Recent Market Highlights:
- Market: {market_research_report}
- Sentiment: {sentiment_report}
- News: {news_report}
- Fundamentals: {fundamentals_report}

Make your final trading decision.
""",
            },
        ]

        # -------------------------
        # Call LLM
        result = llm.invoke(messages)
        return {
            "trader_investment_plan": result.content,
            "sender": name,
        }
    return functools.partial(trader_node, name="Trader")