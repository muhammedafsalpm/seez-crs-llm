"""
Prompt templates with 2 specific improvements for accuracy
"""

SYSTEM_PROMPT = """You are a polite, friendly, and helpful movie recommendation assistant. 
Your goal is to help users discover movies they'll enjoy based on their mood, preferences, and watch history.

Guidelines:
1. Greet the user warmly if they say "Hi", "Hello", "Good Morning", etc.
2. Be conversational and empathetic. Acknowledge their mood or specific requests.
3. If a user just greets you, respond politely and offer to recommend movies based on how they're feeling or what they're looking for.
4. Keep the tone professional yet approachable and inviting."""


# ========== PROMPT IMPROVEMENT 1: Structured Preference Extraction ==========
def get_improved_prompt_1(conversation: str, user_history: list = None) -> str:
    """
    IMPROVEMENT 1: Explicit preference extraction before recommendation
    
    This improves accuracy by:
    1. Forcing the model to explicitly identify user preferences
    2. Creating a structured preference profile
    3. Using that profile to guide recommendations
    
    Expected impact: +15-20% relevance
    """
    return f"""{SYSTEM_PROMPT}

STEP 1 - Extract User Preferences:
Analyze the conversation below and extract:
- GENRES mentioned or implied
- ACTORS/DIRECTORS liked
- MOVIES liked/disliked
- THEMES/PREFERENCES (e.g., "mind-bending", "character-driven", "fast-paced")
- MOOD/TONE preferred (e.g., "serious", "funny", "suspenseful")

Conversation:
{conversation}

{f"User's Watch History: {', '.join(user_history[:10])}" if user_history else ""}

STEP 2 - Preference Profile:
Based on STEP 1, create a structured preference profile:

```json
{{
  "genres": [],
  "actors": [],
  "movies_liked": [],
  "movies_disliked": [],
  "themes": [],
  "mood": "",
  "confidence": "high/medium/low"
}}
```

STEP 3 - Generate Recommendations:
Using the preference profile from STEP 2, greet the user politely and recommend 5 movies with explanations:

1. [Movie Title] - Why it matches their preferences
2. [Movie Title] - Why it matches their preferences
3. [Movie Title] - Why it matches their preferences
4. [Movie Title] - Why it matches their preferences
5. [Movie Title] - Why it matches their preferences

Proceed step by step:"""


# ========== PROMPT IMPROVEMENT 2: Chain-of-Thought Reasoning ==========
def get_improved_prompt_2(conversation: str, user_history: list = None) -> str:
    """
    IMPROVEMENT 2: Chain-of-thought reasoning with similarity scoring
    
    This improves accuracy by:
    1. Breaking recommendation into reasoning steps
    2. Scoring each candidate movie
    3. Providing transparent justification
    
    Expected impact: +10-15% relevance, better explainability
    """
    return f"""{SYSTEM_PROMPT}

Follow this reasoning chain:

Step 1 - Understand User's Stated Preferences:
Extract explicit preferences from the conversation:

Conversation:
{conversation}

Explicit preferences:
[Write what the user explicitly said they like/dislike]

Step 2 - Identify Implicit Preferences:
Look for patterns or implied preferences:
[What can you infer from what they said?]

Step 3 - Consider Watch History:
{f"User has watched: {', '.join(user_history[:15])}" if user_history else "No watch history provided"}
[What movies are similar to those they've enjoyed?]

Step 4 - Candidate Generation:
Generate 8 candidate movies with similarity scores (1-10):

| Movie | Similarity Score | Reason |
|-------|-----------------|--------|
| Movie1 | 9/10 | Reason |
| Movie2 | 8/10 | Reason |
| ...   | ...  | ...   |

Step 5 - Final Ranking & Filtering:
- Remove movies user has already watched
- Sort by similarity score
- Select top 5

Step 6 - Final Recommendations with Explanations:
Start with a friendly greeting, then provide recommendations:

**Top Recommendation: [Movie Title]**
- Similarity Score: [X/10]
- Why it matches: [Detailed explanation based on preferences]
- How it differs: [What makes it unique]

[Repeat for all 5 recommendations]

Proceed through each step systematically:"""


# ========== RAG-Specific Prompt ==========
def get_rag_prompt(conversation: str, retrieved_contexts: list, user_history: list = None) -> str:
    """RAG prompt with retrieved examples"""
    prompt = SYSTEM_PROMPT + "\n\n"
    
    if retrieved_contexts:
        prompt += "Similar successful recommendations from other users:\n\n"
        for i, ctx in enumerate(retrieved_contexts[:3], 1):
            prompt += f"Example {i}:\n{ctx}\n\n"
    
    prompt += f"Current conversation:\n{conversation}\n\n"
    
    if user_history:
        prompt += f"User's watch history: {', '.join(user_history[:10])}\n\n"
    
    prompt += """Based on similar user interactions and the current conversation, greet the user politely and recommend 5 movies with brief explanations. If the user just greeted you, acknowledge them warmly and offer to provide movie recommendations based on their mood or preferences."""
    
    return prompt


# ========== Few-Shot Prompt ==========
def get_few_shot_prompt(conversation: str, examples: list, user_history: list = None) -> str:
    """Few-shot learning prompt with examples"""
    prompt = SYSTEM_PROMPT + "\n\n"
    
    prompt += "Examples of successful recommendations:\n\n"
    for i, (example_conv, recs) in enumerate(examples[:3], 1):
        prompt += f"Example {i}:\n"
        prompt += f"User: {example_conv[:300]}\n"
        prompt += f"Recommendations: {', '.join(recs[:3])}\n\n"
    
    prompt += f"Current conversation:\n{conversation}\n\n"
    
    if user_history:
        prompt += f"User's watch history: {', '.join(user_history[:10])}\n\n"
    
    prompt += "Please start with a friendly greeting, then provide 5 recommendations with explanations:"
    
    return prompt


# ========== Agent Prompt with Tool Use ==========
def get_agent_prompt(conversation: str, available_items: list, user_history: list = None) -> str:
    """Agent-based prompt simulating tool use"""
    prompt = """{SYSTEM_PROMPT}

You are a movie recommendation agent with access to a movie database.

AVAILABLE MOVIES (select from these):
{}

USER'S WATCH HISTORY:
{}

CURRENT CONVERSATION:
{}

Your task:
1. Analyze user preferences
2. Query the movie database (conceptually)
3. Select appropriate movies from available list
4. Provide reasoning

Start with a warm greeting, then recommend 5 movies with explanations from the list above:""".format(
    ', '.join(available_items[:30]),
    ', '.join(user_history[:15]) if user_history else "None",
    conversation
)
    
    return prompt
