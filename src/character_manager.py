from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import json

class CharacterProfile(BaseModel):
    name: str = Field(..., description="Full character name")
    role: str = Field(default="Protagonist", description="Role in story (Protagonist, Antagonist, Foil, Mentor, etc.)")
    archetype: str = Field(default="Reluctant Hero", description="Narrative archetype")
    core_desire: str = Field(default="", description="External Want / Goal")
    inner_need: str = Field(default="", description="Internal Need / Growth target")
    fatal_flaw: str = Field(default="", description="Psychological weakness")
    speech_tics: List[str] = Field(default_factory=list, description="Vocal habits or fillers")
    vocabulary_register: str = Field(default="Standard", description="Register (e.g. Academic, Street-smart, Curt)")
    signature_phrases: List[str] = Field(default_factory=list, description="Memorable catchphrases or habits")
    backstory_hook: str = Field(default="", description="Defining past event")
    voice_guidelines: str = Field(default="", description="Summary of how character speaks in scenes")

    def to_xml_voice_snippet(self) -> str:
        """Renders a token-efficient XML snippet for prompt injection."""
        tics_str = ", ".join(self.speech_tics) if self.speech_tics else "None specified"
        phrases_str = "; ".join(f'"{p}"' for p in self.signature_phrases) if self.signature_phrases else "None"
        
        return (
            f'<character_voice name="{self.name}" role="{self.role}">\n'
            f'  <register>{self.vocabulary_register}</register>\n'
            f'  <speech_tics>{tics_str}</speech_tics>\n'
            f'  <signature_phrases>{phrases_str}</signature_phrases>\n'
            f'  <fatal_flaw>{self.fatal_flaw}</fatal_flaw>\n'
            f'  <voice_guidelines>{self.voice_guidelines}</voice_guidelines>\n'
            f'</character_voice>'
        )

class CharacterManager:
    def __init__(self):
        self.characters: Dict[str, CharacterProfile] = {}

    def add_character(self, profile: CharacterProfile) -> None:
        self.characters[profile.name] = profile

    def get_character(self, name: str) -> Optional[CharacterProfile]:
        return self.characters.get(name)

    def remove_character(self, name: str) -> bool:
        if name in self.characters:
            del self.characters[name]
            return True
        return False

    def list_characters(self) -> List[CharacterProfile]:
        return list(self.characters.values())

    def format_voice_context(self, character_names: List[str]) -> str:
        """Formats selected active characters into compact XML block."""
        snippets = []
        for name in character_names:
            char = self.get_character(name)
            if char:
                snippets.append(char.to_xml_voice_snippet())
        
        if not snippets:
            return "<character_voices>No specific character voice constraints set.</character_voices>"
        
        return "\n".join(snippets)

    def to_json_dict(self) -> dict:
        return {name: char.model_dump() for name, char in self.characters.items()}

    def load_from_json_dict(self, data: dict) -> None:
        self.characters = {}
        for name, char_data in data.items():
            self.characters[name] = CharacterProfile(**char_data)
