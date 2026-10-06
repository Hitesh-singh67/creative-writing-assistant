import streamlit as st
import json
import os
from pathlib import Path

from src.story_engine import StoryEngine
from src.character_manager import CharacterManager, CharacterProfile
from src.metrics import MetricsTracker

# --- Page Configuration ---
st.set_page_config(
    page_title="Narrative Branching Engine & Writing Assistant",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS Styling ---
st.markdown("""
<style>
    /* Dark Glassmorphism Styling */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Main Headers */
    h1, h2, h3 {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .card-accent-blue {
        border-left: 4px solid #3b82f6 !important;
    }
    .card-accent-purple {
        border-left: 4px solid #8b5cf6 !important;
    }
    .card-accent-amber {
        border-left: 4px solid #f59e0b !important;
    }
    .card-accent-emerald {
        border-left: 4px solid #10b981 !important;
    }
    .card-accent-rose {
        border-left: 4px solid #f43f5e !important;
    }
    
    /* Custom Metric Cards */
    .metric-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        background: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
    
    /* Code Blocks / Textarea */
    .stTextArea textarea {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
        font-family: 'Fira Code', 'Courier New', monospace;
    }
    
    /* Tag Badges */
    .tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
        background-color: #334155;
        color: #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "story_engine" not in st.session_state:
    st.session_state.story_engine = StoryEngine()

if "character_manager" not in st.session_state:
    st.session_state.character_manager = CharacterManager()
    # Add initial demo characters for instant playability
    st.session_state.character_manager.add_character(CharacterProfile(
        name="Elena Rostova",
        role="Protagonist",
        archetype="Disgraced Archivist",
        core_desire="Expose the black-market memory trade",
        inner_need="Overcome guilt regarding her brother's memory wipe",
        fatal_flaw="Compulsive obsession with verifying truth",
        speech_tics=["Uses precise technical timestamps", "Pauses abruptly before agreeing"],
        vocabulary_register="Academic / Clinical",
        signature_phrases=["Check the hash signature.", "Unverified data is poison."],
        backstory_hook="Exiled from the Central Archives after leaking classified audit logs.",
        voice_guidelines="Speaks with sharp, measured precision. Never uses slang or filler words."
    ))
    st.session_state.character_manager.add_character(CharacterProfile(
        name="Arthur Pendelton",
        role="Antagonist / Shadow Ally",
        archetype="Pragmatic Broker",
        core_desire="Maintain control over the sector's memory grid",
        inner_need="Acknowledge his own moral corruption",
        fatal_flaw="Cynical utilitarianism",
        speech_tics=["Chuckles dryly when challenged", "Frequently uses financial metaphors"],
        vocabulary_register="Street-smart / Corporate",
        signature_phrases=["Everything has a market rate.", "Sentiments don't pay rent."],
        backstory_hook="Built the first memory exchange network after the Great Wipe.",
        voice_guidelines="Speaks in casual, smooth tones with underlying menace. Deflects questions with counter-offers."
    ))

if "metrics" not in st.session_state:
    st.session_state.metrics = MetricsTracker()

if "active_premise" not in st.session_state:
    st.session_state.active_premise = {
        "premise": "In a neon-drenched metropolis where memories are traded like commodities, a disgraced archivist uncovers a black-market memory capsule containing evidence of her own murder—scheduled for tomorrow midnight.",
        "thematic_conflict": "Authentic Identity vs. Manufactured Comfort",
        "world_rules": "- Rule 1: Memories degrade each time they are transferred.\n- Rule 2: Social standing dictates memory storage bandwidth.\n- Rule 3: Corporate wipe-teams patrol abandoned sectors.",
        "plot_hooks": [
            "1. Elena discovers a encrypted key inside a broker's vault.",
            "2. Arthur offers a truce in exchange for wiping a specific record.",
            "3. The sector server initiates a 24-hour total wipe sequence."
        ]
    }

if "active_scene_text" not in st.session_state:
    st.session_state.active_scene_text = (
        "The rain rattled against the reinforced glass panel like a volley of loose gravel. "
        "Inside the damp server room, Elena kept her fingers resting on the manifold, tapping out a steady four-beat rhythm.\n\n"
        "\"The clearance code was revoked three hours ago, Elena,\" Arthur said, stepping out of the shadows. "
        "His coat glistened with condensation.\n\n"
        "Elena didn't turn around. \"Three hours and twelve minutes, Arthur. Which means whoever signed the warrant hasn't checked the redundant logs yet.\""
    )

if "active_branches" not in st.session_state:
    st.session_state.active_branches = []

# --- Sidebar ---
with st.sidebar:
    st.title("✍️ Narrative Engine")
    st.markdown("---")
    
    # Engine Status Badge
    if st.session_state.story_engine.is_mock:
        st.warning("⚡ **Engine Status**: Mock Mode (Deterministic & Fast)")
        st.caption("No API Key detected in `.env`. Using high-fidelity local narrative generator.")
    else:
        st.success("🟢 **Engine Status**: Gemini AI Online")
        st.caption("Connected via `google-genai` SDK.")
        
    st.markdown("---")
    
    # Active Project Quick Glance
    st.subheader("📖 Project State")
    char_count = len(st.session_state.character_manager.list_characters())
    word_count = len(st.session_state.active_scene_text.split())
    
    st.markdown(f"""
    - **Genre**: Sci-Fi / Cyberpunk Noir
    - **Characters**: `{char_count} profiles`
    - **Scene Word Count**: `{word_count} words`
    """)
    
    st.markdown("---")
    
    # Real-time Velocity Metrics Summary
    st.subheader("⚡ Velocity Metrics")
    summary = st.session_state.metrics.get_summary()
    st.metric(label="Drafting Velocity Multiplier", value=summary["estimated_speedup"])
    st.metric(label="Total Words Drafted", value=summary["words_generated"])
    st.metric(label="Writer's Block Unblocks", value=summary["unblock_sessions"])
    
    st.markdown("---")
    st.caption("Creative Writing Assistant v1.0 • Built with Streamlit & Gemini API")

# --- Main App Header ---
st.title("Creative Writing Assistant & Narrative Branching Engine")
st.markdown("Accelerate fiction drafting through structured prompt chaining, character voice enforcement, and multi-path scene branching.")

# --- Tab Layout ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🌌 Story Genesis", 
    "🎭 Character Bible", 
    "⚡ Scene & Dialogue Co-Pilot", 
    "📊 Export & Velocity Metrics"
])

# ==========================================
# TAB 1: STORY GENESIS
# ==========================================
with tab1:
    st.header("Story Genesis & World Building")
    st.markdown("Configure high-concept seed ideas, genre parameters, and strict anti-cliché negative constraints to generate unique story premises.")
    
    col_input, col_output = st.columns([1, 1])
    
    with col_input:
        st.markdown("### 🎛️ Parameters")
        genre = st.selectbox("Story Genre", [
            "Sci-Fi / Cyberpunk", "Dark Fantasy", "Psychological Thriller", 
            "Noir Mystery", "Romantasy", "Historical Fiction", "Dystopian"
        ])
        
        tone = st.selectbox("Narrative Tone", [
            "Gritty & Atmospheric", "High-Octane & Tense", "Melancholy & Poetic", 
            "Cynical & Satirical", "Whimsical & Ethereal"
        ])
        
        seed_idea = st.text_area(
            "Seed Concept / Core Premise", 
            height=100,
            value="A disgraced archivist in a city where memories are traded like cryptos finds a capsule containing her own murder scheduled for tomorrow."
        )
        
        negative_constraints = st.text_area(
            "Anti-Cliché Negative Constraints",
            height=80,
            value="No chosen one prophecy; No mysterious hooded figure in a tavern; No passive protagonist; No generic evil syndicate without clear motives."
        )
        
        if st.button("🚀 Generate Story Premise", use_container_width=True):
            with st.spinner("Synthesizing high-concept story premise..."):
                res = st.session_state.story_engine.generate_world_premise(
                    seed_idea=seed_idea,
                    genre=genre,
                    tone=tone,
                    negative_constraints=negative_constraints
                )
                st.session_state.active_premise = res
                st.session_state.metrics.record_premise()
                st.toast("New story premise generated!", icon="✨")

    with col_output:
        st.markdown("### 📜 Generated Premise & World Rules")
        premise_data = st.session_state.active_premise
        
        st.markdown(f"""
        <div class="glass-card card-accent-blue">
            <h4 style="margin-top:0; color:#60a5fa;">Core Premise Hook</h4>
            <p style="font-size:1.1rem; line-height:1.6;">{premise_data.get('premise')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="glass-card card-accent-purple">
            <h4 style="margin-top:0; color:#c084fc;">Thematic Friction</h4>
            <p><strong>{premise_data.get('thematic_conflict')}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="glass-card card-accent-amber">
            <h4 style="margin-top:0; color:#fbbf24;">Atmospheric World Rules</h4>
            <pre style="background:transparent; color:#f3f4f6; border:none; padding:0;">{premise_data.get('world_rules')}</pre>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📌 Narrative Plot Hooks"):
            hooks = premise_data.get('plot_hooks', [])
            if isinstance(hooks, list):
                for h in hooks:
                    st.markdown(f"- {h}")
            else:
                st.markdown(hooks)

# ==========================================
# TAB 2: CHARACTER BIBLE
# ==========================================
with tab2:
    st.header("Character Bible & Voice Constraint Generator")
    st.markdown("Build deep psychological character profiles that prevent 'same-voice syndrome' during scene generation.")
    
    col_create, col_list = st.columns([1, 1])
    
    with col_create:
        st.markdown("### ➕ Create / Auto-Generate Character")
        
        char_concept = st.text_input("Character Concept", value="A street-smart memory broker who trades in forgotten childhood memories")
        char_role = st.selectbox("Story Role", ["Protagonist", "Antagonist", "Foil", "Mentor", "Catalyst / Wildcard"])
        char_archetype = st.selectbox("Archetype", ["Reluctant Hero", "Cynical Broker", "Tragic Scholar", "Shadow Ally", "Ruthless Operator"])
        
        if st.button("🪄 Auto-Generate Full Character Sheet", use_container_width=True):
            with st.spinner("Building psychological character profile..."):
                profile = st.session_state.story_engine.generate_character_sheet(
                    character_concept=char_concept,
                    role=char_role,
                    archetype=char_archetype,
                    story_context=st.session_state.active_premise.get("premise", "")
                )
                st.session_state.character_manager.add_character(profile)
                st.session_state.metrics.record_character()
                st.toast(f"Character sheet created for {profile.name}!", icon="🎭")

    with col_list:
        st.markdown("### 🗂️ Active Character Profiles")
        characters = st.session_state.character_manager.list_characters()
        
        if not characters:
            st.info("No character profiles created yet.")
        else:
            for char in characters:
                with st.expander(f"👤 {char.name} ({char.role} • {char.archetype})", expanded=True):
                    st.markdown(f"**Want (Core Desire):** {char.core_desire}")
                    st.markdown(f"**Need (Inner Need):** {char.inner_need}")
                    st.markdown(f"**Fatal Flaw:** <span style='color:#f87171;'>{char.fatal_flaw}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Vocabulary Register:** `{char.vocabulary_register}`")
                    st.markdown(f"**Speech Tics:** {', '.join(char.speech_tics) if char.speech_tics else 'None'}")
                    st.markdown(f"**Voice Guidelines:** {char.voice_guidelines}")
                    
                    st.markdown("#### Token-Efficient XML Voice Snippet")
                    st.code(char.to_xml_voice_snippet(), language="xml")
                    
                    if st.button(f"🗑️ Delete {char.name}", key=f"del_{char.name}"):
                        st.session_state.character_manager.remove_character(char.name)
                        st.rerun()

# ==========================================
# TAB 3: SCENE & DIALOGUE CO-PILOT
# ==========================================
with tab3:
    st.header("Scene & Dialogue Co-Pilot")
    st.markdown("Interactive editor with active character voice injection and instant Narrative Branching to break writer's block.")
    
    col_editor, col_copilot = st.columns([1.2, 0.8])
    
    with col_editor:
        st.markdown("### ✍️ Interactive Scene Editor")
        
        # Textarea for writing scene
        scene_input = st.text_area(
            "Draft your scene here...",
            value=st.session_state.active_scene_text,
            height=380,
            key="scene_editor_textarea"
        )
        st.session_state.active_scene_text = scene_input
        
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            words = len(scene_input.split()) if scene_input else 0
            st.caption(f"📝 Current Word Count: `{words} words`")
        with col_w2:
            if st.button("💾 Record Drafted Words"):
                st.session_state.metrics.record_words(words)
                st.toast(f"Recorded {words} words to velocity metrics!", icon="📈")

    with col_copilot:
        st.markdown("### ⚡ Dialogue & Voice Generator")
        
        # Character selection for voice injection
        all_chars = [c.name for c in st.session_state.character_manager.list_characters()]
        selected_chars = st.multiselect("Select Active Characters in Scene", all_chars, default=all_chars[:2] if len(all_chars)>=2 else all_chars)
        
        dialogue_goal = st.text_input("Scene / Dialogue Goal", value="Elena confronts Arthur about the missing ledger without accusing him directly.")
        
        if st.button("🎙️ Generate Character Dialogue", use_container_width=True):
            with st.spinner("Injecting character voices & subtext..."):
                voice_xml = st.session_state.character_manager.format_voice_context(selected_chars)
                generated_scene = st.session_state.story_engine.generate_scene_dialogue(
                    scene_context=st.session_state.active_scene_text,
                    character_voices_xml=voice_xml,
                    dialogue_goal=dialogue_goal
                )
                st.session_state.active_scene_text += f"\n\n{generated_scene}"
                st.session_state.metrics.record_words(len(generated_scene.split()))
                st.rerun()

        st.markdown("---")
        st.markdown("### 🧱 Break Writer's Block (3 Multi-Path Branches)")
        st.caption("Generate 3 distinct narrative paths forward: Escalation, Complication, Reversal.")
        
        if st.button("💥 Break Writer's Block Now", use_container_width=True):
            with st.spinner("Analyzing dramatic tension & generating 3 narrative branches..."):
                voice_xml = st.session_state.character_manager.format_voice_context(selected_chars)
                branches = st.session_state.story_engine.generate_narrative_branches(
                    current_scene=st.session_state.active_scene_text,
                    character_profiles=voice_xml,
                    story_goal=dialogue_goal
                )
                st.session_state.active_branches = branches
                st.session_state.metrics.record_unblock()
                st.toast("3 Narrative Branch Options Generated!", icon="⚡")

    # Render Branch Options below editor if available
    if st.session_state.active_branches:
        st.markdown("---")
        st.markdown("### 🌿 Choose a Narrative Branch to Apply")
        
        b_cols = st.columns(3)
        colors = ["card-accent-rose", "card-accent-amber", "card-accent-emerald"]
        
        for idx, branch in enumerate(st.session_state.active_branches):
            col = b_cols[idx % 3]
            color_class = colors[idx % 3]
            
            with col:
                st.markdown(f"""
                <div class="glass-card {color_class}">
                    <span class="metric-badge">{branch.get('type', 'Branch')} • Tension {branch.get('dramatic_tension', 8)}/10</span>
                    <h4 style="margin-top:10px; margin-bottom:5px;">{branch.get('title')}</h4>
                    <p style="font-size:0.9rem; color:#cbd5e1; min-height:60px;">{branch.get('summary')}</p>
                    <p style="font-size:0.85rem; font-style:italic; color:#93c5fd;">Dialogue Starter: {branch.get('dialogue_starter')}</p>
                    <p style="font-size:0.8rem; color:#fca5a5;">Consequence: {branch.get('consequence')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"📥 Apply '{branch.get('title')}'", key=f"btn_branch_{idx}", use_container_width=True):
                    branch_addition = f"\n\n/* NARRATIVE BRANCH: {branch.get('title')} ({branch.get('type')}) */\n{branch.get('dialogue_starter')}\n\n"
                    st.session_state.active_scene_text += branch_addition
                    st.session_state.metrics.record_branch_applied()
                    st.toast(f"Applied '{branch.get('title')}' to active draft!", icon="✅")
                    st.rerun()

# ==========================================
# TAB 4: EXPORT & METRICS
# ==========================================
with tab4:
    st.header("Drafting Velocity Metrics & Project Export")
    
    col_m1, col_m2 = st.columns([1, 1])
    
    with col_m1:
        st.markdown("### 📊 Drafting Velocity Breakdown")
        m_summary = st.session_state.metrics.get_summary()
        
        st.markdown(f"""
        <div class="glass-card card-accent-emerald">
            <h3 style="margin-top:0; color:#34d399;">Estimated Speedup: {m_summary['estimated_speedup']}</h3>
            <p>Your creative drafting velocity is accelerated by structured prompt chaining and real-time narrative unblocking.</p>
            <ul>
                <li>Total Words Drafted: <strong>{m_summary['words_generated']}</strong></li>
                <li>Writer's Block Sessions Resolved: <strong>{m_summary['unblock_sessions']}</strong></li>
                <li>Narrative Branches Applied: <strong>{m_summary['branches_applied']}</strong></li>
                <li>Story Premises Generated: <strong>{m_summary['premises_created']}</strong></li>
                <li>Character Sheets Created: <strong>{m_summary['characters_created']}</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown("### 📥 Export Project Manuscript & Bible")
        st.markdown("Download your complete story premise, character sheets, and scene draft formatted in clean Markdown.")
        
        # Assemble Markdown export string
        export_md = f"# Story Manuscript & Narrative Bible\n\n"
        export_md += f"## 1. World Premise & Setting\n"
        export_md += f"**Premise:** {st.session_state.active_premise.get('premise')}\n\n"
        export_md += f"**Thematic Conflict:** {st.session_state.active_premise.get('thematic_conflict')}\n\n"
        export_md += f"### World Rules\n{st.session_state.active_premise.get('world_rules')}\n\n"
        
        export_md += f"## 2. Character Profiles\n"
        for char in st.session_state.character_manager.list_characters():
            export_md += f"### {char.name} ({char.role})\n"
            export_md += f"- **Archetype:** {char.archetype}\n"
            export_md += f"- **Want vs Need:** {char.core_desire} / {char.inner_need}\n"
            export_md += f"- **Fatal Flaw:** {char.fatal_flaw}\n"
            export_md += f"- **Vocabulary Register:** {char.vocabulary_register}\n"
            export_md += f"- **Voice Guidelines:** {char.voice_guidelines}\n\n"
            
        export_md += f"## 3. Active Scene Draft\n\n"
        export_md += st.session_state.active_scene_text
        
        st.download_button(
            label="📄 Download Manuscript (.md)",
            data=export_md,
            file_name="narrative_manuscript.md",
            mime="text/markdown",
            use_container_width=True
        )
        
        st.download_button(
            label="📝 Download Manuscript (.txt)",
            data=export_md,
            file_name="narrative_manuscript.txt",
            mime="text/plain",
            use_container_width=True
        )
