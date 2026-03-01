# FinTalk - Demo Video Speaking Script
**Word-for-word script - Read exactly as written**
**Duration: 5 minutes**

---

## EXACT LINES TO SPEAK:

---

### [OPENING - 20 seconds]

Hello! Today I'm presenting FinTalk - a conversational AI that lets you query two hundred fifty thousand payment transactions using plain English. No SQL, no dashboards, just natural conversation.

---

### [QUICK OVERVIEW - 30 seconds]

FinTalk has four key capabilities: Intent Recognition that classifies questions into descriptive, comparative, segmentation, and risk analysis. Context-Aware Conversations that remember what you asked before. Real-Time Analysis on massive datasets. And LLM-Enhanced Responses with OpenAI integration.

The architecture is simple: SQLite database with SQLAlchemy ORM, a custom NLP layer for intent recognition, a query builder for analysis, FastAPI for the API layer, and Streamlit for the frontend. Built with Python, FastAPI, Pandas, and OpenAI.

---

### [LIVE DEMO - 3.5 minutes]

Now let me show you FinTalk in action.

**[Show terminal - server already running]**

The FastAPI server is running on port eight thousand with our database loaded.

**[Show Streamlit interface]**

Here's our Streamlit interface. Let's start querying.

**[Type first query]**

"What's the average transaction amount for Food category?"

**[Wait for response]**

FinTalk identified the Food category, ran the analysis, and returned rupees four fifty-two as the average with full statistics. Processed in under five hundred milliseconds.

**[Type second query]**

"Compare iOS versus Android payment patterns"

**[Wait for response]**

Perfect. It's comparing device types with transaction volumes, averages, and fraud rates in a business-friendly format.

**[Type third query - MOST IMPORTANT]**

Now watch this - I'll just ask: "How about Entertainment?"

**[Wait for response]**

I never said what to compare, but FinTalk remembered the previous context and automatically compared Entertainment category with the same metrics. This is context-awareness in action.

**[Type fourth query]**

"Break down by state"

**[Wait for response]**

It maintained the Entertainment context and segmented by state. Maharashtra leads with over fifteen thousand transactions.

**[Type fifth query]**

"Show fraud rate for UPI"

**[Wait for response]**

Fraud analysis complete - patterns identified, rates calculated, high-risk categories flagged.

**[Show conversation history briefly]**

All conversation history is preserved here for review or export.

---

### [CLOSING - 30 seconds]

FinTalk democratizes data analytics through natural language. Built with FastAPI, SQLAlchemy, and OpenAI, it delivers instant insights from two hundred fifty thousand transactions with context-aware conversations and zero setup required.

The system handles descriptive queries, comparisons, segmentation, and risk analysis - all while maintaining conversation context across multiple turns.

Thank you for watching!

---

## TIMING GUIDE:
- **0:00 - 0:20**: Opening
- **0:20 - 0:50**: Quick Overview
- **0:50 - 4:20**: Live Demo (70% of video!)
- **4:20 - 4:50**: Closing

**Total: 5 minutes sharp**

---

## DEMO QUERIES (Copy-Paste Ready):
1. `What's the average transaction amount for Food category?`
2. `Compare iOS versus Android payment patterns`
3. `How about Entertainment?`
4. `Break down by state`
5. `Show fraud rate for UPI`

---

## DELIVERY TIPS:
- Speak clearly and with energy - you have limited time
- Read each query BEFORE typing so viewers follow along
- Emphasize the context-aware query (#3) - it's your killer feature
- Don't wait too long for responses - keep momentum
- If loading takes time, briefly explain what's happening

---

## PRE-DEMO CHECKLIST:
- [ ] Have FastAPI server already running in background
- [ ] Have Streamlit UI already loaded and visible
- [ ] Clear any previous conversation history
- [ ] Test all 5 queries beforehand to ensure they work
- [ ] Have queries ready to copy-paste (for speed)

---

**Remember: Focus on the DEMO - that's what impresses judges! 🚀**
