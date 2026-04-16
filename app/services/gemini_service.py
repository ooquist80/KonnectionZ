import json
from datetime import datetime

import httpx

from app.core.config import get_settings
from app.db.client import DatabaseClient
from app.models import gameset
from app.models.wordset import WordsetWrite
from app.repositories.gameset_repository import GameSetRepository
from app.repositories.wordset_repository import WordsetRepository

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"


class GeminiService:

    def __init__(self, database_client: DatabaseClient):
        self.gemini_api_key = get_settings().gemini_api_key
        self.wordset_repository = WordsetRepository(database_client)
        self.gameset_repository = GameSetRepository(database_client)

    def create_full_gameset(self, language: str):
        puzzle = self.generate_valid_puzzle(language)
        wordsets = self.create_wordsets(puzzle)
        gameset_write = gameset.GameSetWrite(
            name=f"AI Puzzle {datetime.today().isoformat()}",
            date=datetime.today(),
            daily_date=datetime.today(),
            wordsets=[ws.id for ws in wordsets])
        return self.gameset_repository.create(date=gameset_write.date,
                                              daily_date=gameset_write.daily_date,
                                              name=gameset_write.name,
                                              wordset_ids=gameset_write.wordsets)

    def create_wordsets(self, puzzle):
        wordsets = []
        for group in puzzle["groups"]:
            wordset = WordsetWrite(category=group["theme"],
                                   words=group["words"],
                                   difficulty=1)
            wordsets.append(self.wordset_repository.create(wordset))
        return wordsets

    def validate_puzzle(self, puzzle):
        try:
            groups = puzzle["groups"]
            if len(groups) != 4:
                return False

            words = [w for g in groups for w in g["words"]]
            if len(set(words)) != 16:
                return False
            themes = [g["theme"] for g in groups]
            if not all([len(t) <= 30 for t in themes]):
                return False
        except Exception:
            return False
        else:
            return True

    def generate_valid_puzzle(self, language="en"):
        for _ in range(3):
            raw = self.generate_puzzle(language)
            puzzle = json.loads(raw)

            if self.validate_puzzle(puzzle):
                return puzzle

        raise Exception("Failed to generate valid puzzle")

    def generate_puzzle(self, language: str = "en"):
        prompt = self.build_prompt(language)

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "object",
                    "properties": {
                        "groups": {
                            "type": "array",
                            "minItems": 4,
                            "maxItems": 4,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "difficulty": {
                                        "type": "string",
                                        "enum": ["easy", "medium", "hard", "very_hard"]
                                    },
                                    "theme": {"type": "string", "maxLength": 30},
                                    "words": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "minItems": 4,
                                        "maxItems": 4
                                    }
                                },
                                "required": ["difficulty", "theme", "words"]
                            }
                        }
                    },
                    "required": ["groups"]
                }
            }
        }

        with httpx.Client() as client:
            response = client.post(
                f"{GEMINI_URL}?key={self.gemini_api_key}",
                json=payload,
                timeout=300
            )
            response.raise_for_status()
            data = response.json()

        # Extract model text safely
        text = data["candidates"][0]["content"]["parts"][0]["text"]

        return text

    def build_prompt(self, language: str) -> str:
        today = datetime.today().isoformat()

        if language == "sv":
            return f"""
            Generera ett Connections-liknande ordspel på svenska.
            
            Datum: {today}
            
            Du måste skapa EXAKT 4 grupper:
            
            1. LÄTT (gul)
            - kräver eftertanke            
            
            2. MEDEL (grön)
            - kräver eftertanke
            - minst ett ord kan passa flera grupper
            
            3. SVÅR (blå)
            - abstrakt eller mindre uppenbar
            - minst ett ord kan passa flera grupper
            
            4. MYCKET SVÅR (lila)
            - ordlek eller dold regel
            - "aha"-moment
            - minst ett ord kan passa flera grupper
            
            Regler:
            - exakt 16 unika svenska ord
            - inga dubbletter
            - endast enstaka ord
            - undvik egennamn            
            
            Extra:
            - inkludera vilseledande kopplingar
            - kategorier bör vara 1-3 ord inte meningar
            
            Returnera ENDAST JSON.
            """
        else:
            return f"""
            Generate a NYT Connections-style puzzle.
            
            Date: {today}
            
            Create EXACTLY 4 groups:
            
            1. EASY (yellow)
            - clear category
            - no ambiguity
            2. MEDIUM (green)
            - requires reflection
            
            3. HARD (blue)
            - abstract or less obvious
            - at least one word can fit into multiple groups
            
            4. VERY HARD (purple)
            - wordplay or hidden rule
            - "aha"-moment
            
            Rules:
            - 16 unique words
            - No duplicates
            - Single words only
            - Avoid proper nouns
            
            Extra:
            - include misdirection overlap
            - themes are preferably 1-3 words, not sentences
            
            Return ONLY JSON.
            """
