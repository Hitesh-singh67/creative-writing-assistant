# 🚀 LinkedIn Content Pack: Creative Writing Assistant & Narrative Branching Engine

Here are ready-to-post LinkedIn templates crafted for maximum engagement, clear technical authority, and high readability.

---

## 📌 Option 1: High-Engagement Feed Post (Recommended for Main Feed)

**Copy and paste the text below directly into your LinkedIn post:**

---

🚀 Excited to share my latest GenAI project: **Creative Writing Assistant & Narrative Branching Engine**! ✍️🤖

Ever noticed how most LLMs suffer from "same-voice syndrome" when writing fiction? They often spit out formulaic tropes, on-the-nose dialogue, and generic plot lines.

To solve this and help writers overcome creative blocks, I built an interactive Python (Streamlit) web application powered by **Google Gemini API (`google-genai`)** and advanced **prompt engineering architectures**.

### 🌟 Key Highlights & Engineering Features:

1️⃣ **Multi-Path Scene Branching ("Break Writer's Block")**:
When a writer gets stuck, the engine analyzes active scene context and dynamically generates 3 distinct narrative paths forward:
- 💥 **Escalation**: Doubles immediate stakes & urgency.
- 🧩 **Complication**: Introduces unexpected obstacles & secrets.
- 🔄 **Reversal**: Shifts power dynamics or delivers sharp betrayals.

2️⃣ **XML Character Voice Injection (`<character_voice>`)**:
Prevents context bleeding by injecting token-efficient XML snippets containing speech tics, vocabulary registers, and fatal flaws into active scene prompts.

3️⃣ **Anti-Cliché Negative Constraints**:
Strict prompt rules forbidding overused tropes ("The Chosen One who doesn't know their power", passive protagonists, generic evil syndicates).

4️⃣ **Subtext Dialogue Co-Pilot**:
Uses in-context few-shot learning to train the model on subtext-heavy dialogue vs. blunt emotional confessions.

5️⃣ **Deterministic Mock Engine**:
Built-in zero-config fallback mode so the app runs seamlessly out of the box even without API keys!

🛠️ **Tech Stack**: Python 3.12 | Streamlit | Google Gemini API (`google-genai`) | Pydantic | Rich

What prompt engineering techniques do you use to enforce character voice in LLMs? Would love to hear your thoughts! 👇

#GenerativeAI #PromptEngineering #Python #Streamlit #GeminiAPI #LLMs #ArtificialIntelligence #SoftwareEngineering #CreativeWriting #AI

---

## 📰 Option 2: Long-Form Technical Showcase (For LinkedIn Article / Portfolio)

# How I Built a Multi-Path Narrative Branching Engine with Gemini API & Streamlit

### The Problem: Why Standard LLM Prose Fails Fiction Writers
While Large Language Models excel at code and summary, creative writers often run into major roadblocks:
1. **Generic Prose & Clichés**: Unconstrained LLMs defaults to predictable tropes.
2. **On-The-Nose Dialogue**: Characters state their emotions directly rather than evading or deflecting with subtext.
3. **Context Bloat**: Injecting full character backstories quickly wastes context windows.

### The Solution: Modular Prompt Chaining Architecture

To address these challenges, I built an end-to-end writing assistant structured around 4 distinct prompt engineering pipelines:

#### 1. Story Genesis (`world_premise_prompt.txt`)
Synthesizes seed ideas into high-concept hooks, world rules, and thematic friction (e.g., *Authentic Memory vs. Manufactured Comfort*).

#### 2. Psychological Character Bible (`character_bible_prompt.txt`)
Outputs validated JSON character sheets mapping Want (Core Desire) vs. Need (Inner Growth), Fatal Flaw, and Speech Register. Translates full profiles into token-efficient XML snippets for scene injection:

```xml
<character_voice name="Elena Rostova" role="Protagonist">
  <register>Academic / Clinical</register>
  <speech_tics>Uses precise technical timestamps</speech_tics>
  <voice_guidelines>Speaks with sharp, measured precision.</voice_guidelines>
</character_voice>
```

#### 3. Scene & Subtext Dialogue Co-Pilot (`scene_dialogue_prompt.txt`)
Employs contrastive few-shot learning to steer output toward subtext and physical action beats over blunt dialogue.

#### 4. Narrative Branching Engine (`branching_engine_prompt.txt`)
Calculates dramatic tension (1-10) and offers 3 structural branch choices (Escalation, Complication, Reversal) to instantly unblock writers.

---

## 📸 Recommended Post Attachments / Screenshots

To double your LinkedIn reach, attach 1 to 3 images or a quick video/GIF demonstrating:
1. **Screenshot 1**: The Streamlit Tab 3 ("Scene & Dialogue Co-Pilot") showing the 3 color-coded narrative branch cards (*Escalation*, *Complication*, *Reversal*).
2. **Screenshot 2**: The Character Bible XML Voice Snippet view.
3. **Screenshot 3**: The Drafting Velocity Metrics card showing speedup multipliers.
