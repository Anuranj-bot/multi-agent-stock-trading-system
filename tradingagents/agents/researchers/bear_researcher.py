# ===============================
# SAFE IMPORTS
# ===============================
from tradingagents.agents.utils.safety import trim, safe_get, safe_memory_extract


# ===============================
# BEAR RESEARCHER
# ===============================

def create_bear_researcher(llm, memory):

    def bear_node(state) -> dict:

        # -------------------------------
        # SAFE STATE EXTRACTION
        # -------------------------------
        investment_debate_state = safe_get(state, "investment_debate_state", {})

        history = trim(safe_get(investment_debate_state, "history", ""), 2500)
        bear_history = trim(safe_get(investment_debate_state, "bear_history", ""), 2000)
        bull_history = safe_get(investment_debate_state, "bull_history", "")
        current_response = trim(safe_get(investment_debate_state, "current_response", ""), 1200)

        count = safe_get(investment_debate_state, "count", 0) + 1

        # -------------------------------
        # SAFE REPORT EXTRACTION
        # -------------------------------
        market_research_report = trim(safe_get(state, "market_report", ""), 1500)
        sentiment_report = trim(safe_get(state, "sentiment_report", ""), 1200)
        news_report = trim(safe_get(state, "news_report", ""), 1200)
        fundamentals_report = trim(safe_get(state, "fundamentals_report", ""), 1500)

        curr_situation = (
            market_research_report
            + "\n\n"
            + sentiment_report
            + "\n\n"
            + news_report
            + "\n\n"
            + fundamentals_report
        )

        # -------------------------------
        # SAFE MEMORY EXTRACTION
        # -------------------------------
        try:
            past_memories_raw = memory.get_memories(curr_situation, n_matches=2)
            past_memory_str = safe_memory_extract(past_memories_raw, 800)
        except Exception:
            past_memory_str = ""

        # -------------------------------
        # SHORT + CONTROLLED PROMPT
        # -------------------------------
        prompt = f"""
You are a Bear Analyst arguing against buying this stock.

Focus strictly on:
- Risks
- Weak fundamentals
- Negative indicators

Be sharp, analytical, and concise.

Debate History:
{history}

Last Bull Argument:
{current_response}

Lessons from past similar trades:
{past_memory_str}
"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {trim(response.content, 1500)}"

        # -------------------------------
        # SAFE STATE UPDATE
        # -------------------------------
        new_state = {
            "history": trim(history + "\n" + argument, 3500),
            "bear_history": trim(bear_history + "\n" + argument, 2500),
            "bull_history": bull_history,
            "current_response": argument,
            "count": count + 1,
        }

        return {"investment_debate_state": new_state}

    return bear_node
