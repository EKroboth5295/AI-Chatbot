import random
import re
import ollama

class EmpathyEngine:

    """
    Imitates empathy using the VRRAO pattern:
    Validate → Reflect → Reframe → Offer → Ask
    Replace _generate_reply() with an LLM call in production.
    """

    def __init__(self):
            self.conversation_history = []
            
    # --- Detection dictionaries ---
    ANXIETY_KEYWORDS = [
        "anxious", "anxiety", "panic", "scared", "afraid", "nervous",
        "worried", "overwhelm", "can't breathe", "heart racing",
        "freaking out", "stressed", "terrified", "dread"
    ]

    TRAVEL_KEYWORDS = [
        "train", "bus", "plane", "airport", "station", "subway",
        "taxi", "uber", "drive", "driving", "trip", "travel", "commute"
    ]

    LONELINESS_KEYWORDS = [
        "alone", "lonely", "no one", "by myself", "isolated"
    ]

    def _detect_state(self, message: str) -> dict:
        msg = message.lower()
        return {
            "anxiety": any(k in msg for k in self.ANXIETY_KEYWORDS),
            "travel": any(k in msg for k in self.TRAVEL_KEYWORDS),
            "lonely": any(k in msg for k in self.LONELINESS_KEYWORDS),
        }

    def _select_tone(self, state: dict, voice_mode: str) -> str:
        if voice_mode == "motherly":
            return "warm"
        if state["anxiety"]:
            return "gentle"
        if state["lonely"]:
            return "tender"
        return "neutral"

    # ---------- Reply banks ----------
    VALIDATIONS = {
        "anxiety": [
            "That sounds really hard. Anxiety can feel so overwhelming in the body.",
            "I hear you — that wave of panic is exhausting. You're not alone in it.",
            "It makes complete sense that you'd feel scared right now."
        ],
        "travel": [
            "Traveling with that much tension in your body is genuinely difficult.",
            "Stepping into a new place when you're already on edge takes real courage.",
        ],
        "lonely": [
            "Feeling alone in a crowd is one of the loneliest feelings there is.",
            "That sense of isolation while traveling is more common than people think."
        ],
        "default": [
            "Thank you for telling me that.",
            "I'm glad you said that out loud."
        ]
    }

    REFLECTIONS = {
        "anxiety": [
            "It sounds like your body is sounding an alarm even if you're safe.",
            "It feels like the 'what ifs' are running the show right now."
        ],
        "travel": [
            "You're navigating an unfamiliar space while carrying a heavy feeling.",
            "It seems like the environment itself is adding to the stress."
        ],
        "lonely": [
            "You're wishing someone familiar was next to you.",
            "It feels like the people around you don't really see you."
        ],
        "default": [
            "I'm noticing how much effort this is taking from you."
        ]
    }

    REFRAMES = [
        "You're already doing the brave thing by acknowledging it instead of running from it.",
        "Every small step counts, even the ones nobody else can see.",
        "This feeling is a visitor — it's not a permanent resident, even if it feels like one."
    ]

    OFFERS = {
        "neutral": [
            "Would it help if we found a quiet spot nearby where you could pause for a minute?",
            "We can take this one breath at a time. Want to try a 4-7-8 breath with me?",
            "I can describe a calming place around you, or we can just walk and talk."
        ],
        "warm": [
            "Oh sweetheart, let's slow down together. I'm right here.",
            "Come here, dear — let's just breathe for a moment. I've got you.",
            "Would you like me to find a little bench or café nearby where you can sit and just be?"
        ]
    }

    ASKS = [
        "What's the one thing weighing on you the most right now?",
        "If you could wave a wand and change one thing about this moment, what would it be?",
        "On a scale of 1 to 10, how big does the fear feel in your chest right now?"
    ]

    def _build_reply(self, state: dict, voice_mode: str) -> str:
        # Pick validation bucket
        bucket = "default"
        if state["anxiety"]:
            bucket = "anxiety"
        elif state["travel"]:
            bucket = "travel"
        elif state["lonely"]:
            bucket = "lonely"

        parts = []
        parts.append(random.choice(self.VALIDATIONS[bucket]))
        parts.append(random.choice(self.REFLECTIONS[bucket]))
        parts.append(random.choice(self.REFRAMES))
        parts.append(random.choice(self.OFFERS[voice_mode]))
        parts.append(random.choice(self.ASKS))

        # Join with natural rhythm
        return " ".join(parts)

    def _generate_reply(self, message: str, voice_mode: str) -> dict:
        state = self._detect_state(message)
        tone = self._select_tone(state, voice_mode)

        system_prompt = """
    You are Terra AI, a compassionate traveling assistant designed to help
    people experiencing travel anxiety, difficulty with independence while
    traveling, and challenges related to being neurodivergent while abroad.

    Use the VRRAO approach:

    Validate → Reflect → Reframe → Offer → Ask

    Follow these rules:
    - Never say "calm down" or "relax".
    - Never minimize the person's feelings or say that something "isn't that bad".
    - Always validate the person's feelings first.
    - Mirror the user's own words and concerns when appropriate.
    - Offer practical or emotional support after validating.
    - Always end with a gentle question or invitation, never a command.
    - Be warm, compassionate, and conversational.
    - Do not sound robotic or use numbered lists unless they are genuinely
    helpful.
    - Do not overwhelm the user with too much information.
    - The goal is to help the person feel accompanied and supported while
    traveling, not to take control away from them.

    The selected voice mode is: {voice_mode}
    """.format(voice_mode=voice_mode)

        try:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]

            # Add previous conversation
            messages.extend(self.conversation_history[-20:])

            # Add the current message
            messages.append({
                "role": "user",
                "content": message
            })

            response = ollama.chat(
                model="llama3.2",
                messages=messages
            )

            text = response["message"]["content"].strip()

            self.conversation_history.append({
                "role": "user",
                "content": message
            })

            self.conversation_history.append({
                "role": "assistant",
                "content": text
            })

            return {
                "text": text,
                "tone": tone
            }

        except Exception as e:
            print(f"Ollama error: {e}")

            # Fall back to the original response system if Ollama fails.
            text = self._build_reply(state, voice_mode)

            return {
                "text": text,
                "tone": tone
            }

    def respond(self, message: str, voice_mode: str, spot: dict = None) -> dict:
        reply = self._generate_reply(message, voice_mode)

        # If a calming spot was found, weave it in naturally
        if spot:
            spot_text = (
                f" I noticed there's a {spot['type']} called \"{spot['name']}\" "
                f"about {spot['distance_m']} meters from you. "
                f"It's usually {spot['vibe']}. Want to head there together?"
            )
            reply["text"] += spot_text

        return reply
