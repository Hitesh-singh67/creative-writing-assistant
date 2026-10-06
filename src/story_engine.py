import os
import re
import json
import random
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from src.character_manager import CharacterProfile

load_dotenv()

class StoryEngine:
    def __init__(self, prompts_dir: Optional[str] = None):
        self.prompts_dir = Path(prompts_dir) if prompts_dir else Path(__file__).parent.parent / "prompts"
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client = None

        if self.gemini_api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.gemini_api_key)
            except Exception as e:
                print(f"[StoryEngine Warning] Failed to initialize Gemini API client: {e}. Falling back to Mock Mode.")

    @property
    def is_mock(self) -> bool:
        return self.client is None

    def _load_prompt_template(self, filename: str) -> str:
        filepath = self.prompts_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Prompt template file not found at {filepath}")
        return filepath.read_text(encoding="utf-8")

    def _call_llm(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        if self.client:
            try:
                from google.genai import types
                config = types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.9,
                )
                if system_instruction:
                    config.system_instruction = system_instruction

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=config
                )
                return response.text
            except Exception as e:
                print(f"[StoryEngine API Error] {e}. Using intelligent fallback mock generator.")
                return self._generate_fallback_response(prompt)
        else:
            return self._generate_fallback_response(prompt)

    def generate_world_premise(self, seed_idea: str, genre: str, tone: str, negative_constraints: str = "") -> Dict[str, Any]:
        template = self._load_prompt_template("world_premise_prompt.txt")
        prompt = template.format(
            seed_idea=seed_idea,
            genre=genre,
            tone=tone,
            negative_constraints=negative_constraints or "None specified"
        )

        if self.is_mock:
            return self._mock_world_premise(seed_idea, genre, tone)

        raw_output = self._call_llm(prompt)
        return self._parse_xml_world_premise(raw_output)

    def generate_character_sheet(self, character_concept: str, role: str, archetype: str, story_context: str) -> CharacterProfile:
        template = self._load_prompt_template("character_bible_prompt.txt")
        prompt = template.format(
            character_concept=character_concept,
            role=role,
            archetype=archetype,
            story_context=story_context
        )

        if self.is_mock:
            return self._mock_character_sheet(character_concept, role, archetype)

        raw_output = self._call_llm(prompt)
        return self._parse_json_character_sheet(raw_output, character_concept, role, archetype)

    def generate_scene_dialogue(self, scene_context: str, character_voices_xml: str, dialogue_goal: str) -> str:
        template = self._load_prompt_template("scene_dialogue_prompt.txt")
        prompt = template.format(
            scene_context=scene_context,
            character_voices=character_voices_xml,
            dialogue_goal=dialogue_goal
        )

        if self.is_mock:
            return self._mock_scene_dialogue(scene_context, dialogue_goal)

        raw_output = self._call_llm(prompt)
        match = re.search(r"<generated_scene>(.*?)</generated_scene>", raw_output, re.DOTALL)
        if match:
            return match.group(1).strip()
        return raw_output.strip()

    def generate_narrative_branches(self, current_scene: str, character_profiles: str, story_goal: str) -> List[Dict[str, Any]]:
        template = self._load_prompt_template("branching_engine_prompt.txt")
        prompt = template.format(
            current_scene=current_scene,
            character_profiles=character_profiles,
            story_goal=story_goal
        )

        if self.is_mock:
            return self._mock_narrative_branches(current_scene)

        raw_output = self._call_llm(prompt)
        return self._parse_xml_branches(raw_output)

    # --- Parsers ---

    def _parse_xml_world_premise(self, text: str) -> Dict[str, Any]:
        def extract_tag(tag: str, default: str = "") -> str:
            m = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
            return m.group(1).strip() if m else default

        premise = extract_tag("premise", "A gripping high-concept narrative driven by hidden secrets and high stakes.")
        thematic = extract_tag("thematic_conflict", "Survival vs. Morality")
        world_rules = extract_tag("world_rules", "- Reality bends under emotional stress.\n- Information is the highest currency.\n- Trust is strictly conditional.")
        plot_hooks = extract_tag("plot_hooks", "1. An unexpected discovery triggers an immediate countdown.\n2. A former ally resurfaces with a compromised secret.\n3. The primary sanctuary is suddenly declared hostile territory.")

        return {
            "premise": premise,
            "thematic_conflict": thematic,
            "world_rules": world_rules,
            "plot_hooks": plot_hooks,
            "raw_response": text
        }

    def _parse_json_character_sheet(self, text: str, concept: str, role: str, archetype: str) -> CharacterProfile:
        try:
            # Extract JSON block
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return CharacterProfile(**data)
        except Exception as e:
            print(f"[JSON Parse Error] {e}. Falling back to default profile parser.")
        
        return self._mock_character_sheet(concept, role, archetype)

    def _parse_xml_branches(self, text: str) -> List[Dict[str, Any]]:
        pattern = r'<branch_option\s+type=["\'](.*?)["\']>(.*?)</branch_option>'
        matches = re.findall(pattern, text, re.DOTALL)
        
        branches = []
        for branch_type, content in matches:
            title_m = re.search(r"<title>(.*?)</title>", content, re.DOTALL)
            summary_m = re.search(r"<summary>(.*?)</summary>", content, re.DOTALL)
            tension_m = re.search(r"<dramatic_tension>(.*?)</dramatic_tension>", content, re.DOTALL)
            dialogue_m = re.search(r"<dialogue_starter>(.*?)</dialogue_starter>", content, re.DOTALL)
            consequence_m = re.search(r"<consequence>(.*?)</consequence>", content, re.DOTALL)

            branches.append({
                "type": branch_type.strip().capitalize(),
                "title": title_m.group(1).strip() if title_m else f"{branch_type} Twist",
                "summary": summary_m.group(1).strip() if summary_m else "The narrative shifts dramatically.",
                "dramatic_tension": int(re.search(r"\d+", tension_m.group(1)).group(0)) if (tension_m and re.search(r"\d+", tension_m.group(1))) else 8,
                "dialogue_starter": dialogue_m.group(1).strip() if dialogue_m else '"We don\'t have time for this."',
                "consequence": consequence_m.group(1).strip() if consequence_m else "The team must re-evaluate their entire protocol."
            })

        if not branches:
            return self._mock_narrative_branches("Fallback scene context")

        return branches

    # --- Realistic Fallback Mock Generators ---

    def _generate_fallback_response(self, prompt: str) -> str:
        if "world_premise_prompt" in prompt or "<seed_idea>" in prompt:
            return "<premise>In a neon-drenched metropolis where memories are traded like cryptos, a disgraced archivist uncovers a black-market memory capsule containing evidence of their own murder—scheduled for tomorrow midnight. To survive, they must outrun algorithmic assassins while determining which of their recorded memories are real.</premise><thematic_conflict>Authentic Identity vs. Artificial Preservation</thematic_conflict><world_rules>- Memories deteriorate by 5% every time they are transferred.\n- Biological death before memory sync leaves behind ghost traces in public networks.\n- The corporate grid can selectively wipe civic compliance records.</world_rules><plot_hooks>1. The archivist finds a biometric key inside a stranger's chest cavity.\n2. Their primary informant turns out to be a synthetic replica operating on stolen childhood memories.\n3. The orbital grid threatens a full sector wipe in 72 hours.</plot_hooks>"
        elif "character_bible_prompt" in prompt or "<character_concept>" in prompt:
            return json.dumps({
                "name": "Kaelen Vance",
                "role": "Protagonist",
                "archetype": "Reluctant Investigator",
                "core_desire": "Expose the truth behind the stolen memory archives to clear his sister's name.",
                "inner_need": "Learn to trust others after years of betrayals.",
                "fatal_flaw": "Paranoid hyper-fixation on minutiae.",
                "speech_tics": ["Repeats key metrics before answering", "Pauses abruptly before stating hard truths"],
                "vocabulary_register": "Technical and clinical with cynical undercurrents",
                "signature_phrases": ["Let's look at the telemetry.", "Nothing stays buried in the data stream."],
                "backstory_hook": "Dismissed from the Cyber-Forensics Division after refusing to falsify an audit.",
                "voice_guidelines": "Speaks with clipped precision. Uses short, declarative sentences. Avoids emotional jargon."
            })
        elif "scene_dialogue_prompt" in prompt or "<scene_context>" in prompt:
            return "<generated_scene>Kaelen didn't turn around when the elevator chime vibrated through the floorplates. He kept his fingers resting on the server manifold, tapping out a steady four-beat rhythm.\n\n\"The clearance code was revoked three hours ago, Kaelen,\" Mara said, stepping into the damp amber glow of the terminal bay. Her coat was wet with acidic rain.\n\n\"Three hours and twelve minutes,\" Kaelen corrected without raising his voice. \"Which means whoever signed the warrant hasn't checked the redundant logs yet.\"\n\nMara drew off her leather gloves, finger by finger. \"Or they wanted you right where you are. Hand over the drive, Kaelen.\"\n\nKaelen slid the black metal cartridge into his inner pocket, feeling its heavy thermal pulse against his ribs. \"You always did trust the chain of command, Mara. Even when the links were rusted through.\"</generated_scene>"
        else:
            return "<branch_option type=\"Escalation\"><title>Thermal Containment Breach</title><summary>The facility lockdown triggers automatically, trapping both allies and rival agents inside a collapsing sub-level.</summary><dramatic_tension>9</dramatic_tension><dialogue_starter>\"Override code failing in thirty seconds. Get behind the blast shield!\"</dialogue_starter><consequence>All escape routes are sealed; Kaelen must forge an uneasy truce with his pursuers.</consequence></branch_option><branch_option type=\"Complication\"><title>The Decoy Drive Revealed</title><summary>Kaelen discovers the encrypted drive contains a live tracker broadcast pinging their exact position to regional security headquarters.</summary><dramatic_tension>8</dramatic_tension><dialogue_starter>\"That's not data... that's a beacon.\"</dialogue_starter><consequence>They have less than two minutes before strike units breach the perimeter.</consequence></branch_option><branch_option type=\"Reversal\"><title>The Secret Sponsor</title><summary>Mara reveals she isn't working for the corporation, but is acting under orders from Kaelen's presumed-dead sister.</summary><dramatic_tension>10</dramatic_tension><dialogue_starter>\"She told me you'd be wearing that coat, Kaelen. She sent me to bring you in.\"</dialogue_starter><consequence>Kaelen's entire motivation shifts from revenge to uncovering his sister's true allegiance.</consequence></branch_option>"

    def _mock_world_premise(self, seed: str, genre: str, tone: str) -> Dict[str, Any]:
        return {
            "premise": f"In a {tone.lower()} {genre.lower()} world inspired by '{seed}', a disgraced archivist uncovers a black-market memory capsule containing evidence of an impending catastrophe. To survive, they must navigate treacherous factions while questioning their own reality.",
            "thematic_conflict": "Authentic Memory vs. Manufactured Comfort",
            "world_rules": "- Rule 1: Memories degrade each time they are shared or digitized.\n- Rule 2: Social status is directly tied to neural bandwidth purity.\n- Rule 3: Natural weather has been replaced by localized climate contracts.",
            "plot_hooks": [
                "1. A high-ranking official offers amnesty in exchange for an unedited childhood memory.",
                "2. The primary vault where records are stored suffers an intentional power failure.",
                "3. An old friend appears, claiming to have zero recollection of their shared past."
            ],
            "raw_response": "[Generated via Deterministic Creative Engine]"
        }

    def _mock_character_sheet(self, concept: str, role: str, archetype: str) -> CharacterProfile:
        name_parts = ["Vespera Vance", "Cyrus Sterling", "Lyra Vance", "Darius Thorn", "Helena Mercer"]
        name = random.choice(name_parts)
        return CharacterProfile(
            name=name,
            role=role,
            archetype=archetype,
            core_desire=f"Expose the truth behind '{concept}' at any personal cost.",
            inner_need="Overcome deep-seated mistrust and embrace genuine human connection.",
            fatal_flaw="Obsessive obsession with detail and inability to delegate.",
            speech_tics=["Taps knuckles on wooden surfaces", "Uses sharp rhetorical questions when pressured"],
            vocabulary_register="Precise, academic, with terse cadence",
            signature_phrases=["Check the foundation twice.", "Facts don't care for sentiment."],
            backstory_hook="Exiled from the High Guild after uncovering a systemic falsification scandal.",
            voice_guidelines="Speaks in measured, rhythmically deliberate sentences. Avoids hyperbole and rarely raises voice."
        )

    def _mock_scene_dialogue(self, scene_context: str, dialogue_goal: str) -> str:
        return (
            f"The rain rattled against the reinforced glass panel like a volley of loose gravel. "
            f"Inside the dimly lit study, the air tasted of ozone and dry parchment.\n\n"
            f"\"You knew about the discrepancy before the council met, didn't you?\" Vespera's voice was barely louder than the hum of the desk terminal, but it cut cleanly across the room.\n\n"
            f"Cyrus didn't look up from his teacup. He watched the steam curl toward the ceiling joists. \"Knowledge is a heavy cargo, Vespera. You don't load it onto a ship until you're certain of the harbor.\"\n\n"
            f"\"The harbor is burning, Cyrus.\" She took two steps forward, setting her palms flat against the polished oak desk. \"And you're still adjusting the sails.\"\n\n"
            f"Cyrus finally raised his eyes. A faint, tired smile touched the corners of his mouth. \"Then perhaps we should learn how to swim.\""
        )

    def _mock_narrative_branches(self, current_scene: str) -> List[Dict[str, Any]]:
        return [
            {
                "type": "Escalation",
                "title": "Sudden Security Lockdown",
                "summary": "Heavy acoustic shutters slam shut across all exits as a silent distress beacon pings the regional enforcement squad.",
                "dramatic_tension": 9,
                "dialogue_starter": '"We have less than forty seconds before the doors magnetize. Decides now!"',
                "consequence": "The characters must abandon their hidden exit and force their way through the main vault access shaft."
            },
            {
                "type": "Complication",
                "title": "The Compromised Ledger",
                "summary": "Upon opening the encrypted file, they discover half the entries have been overwritten with Vespera's personal signature.",
                "dramatic_tension": 8,
                "dialogue_starter": '"Explain to me why your digital key is timestamped three weeks ago on this transfer."',
                "consequence": "Trust between the allies shatters, forcing a tense re-negotiation of their alliance."
            },
            {
                "type": "Reversal",
                "title": "The Unexpected Ally",
                "summary": "The antagonist's chief enforcer contacts them via private frequency, offering the vault passcode in exchange for asylum.",
                "dramatic_tension": 10,
                "dialogue_starter": '"I don\'t want your cause. I want out of this city before sunrise."',
                "consequence": "The team must choose between trusting a deadly rival or attempting a near-impossible manual breach."
            }
        ]
