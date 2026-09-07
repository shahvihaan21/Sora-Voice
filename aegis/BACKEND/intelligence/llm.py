import asyncio
import datetime
import re
from typing import List, Dict
import httpx
from BACKEND.logger import log
from BACKEND.config import config

class IntelligenceEngine:
    def __init__(self):
        self.host = config.ollama_host.rstrip('/')
        self.model_id = config.ollama_model or "jarvis-ft:latest"
        self.conversation_history: List[Dict[str, str]] = []

        self.system_instruction = (
            "You are Jarvis, a lightning-fast, ultra-smart, elegant, and friendly AI desktop assistant. "
            "You provide concise, highly accurate, and conversational answers. "
            "Speak naturally without markdown formatting, bullet symbols, or robotic phrasing. "
            "Keep voice responses crisp, direct, and under 2-3 sentences unless detailed explanation is requested."
        )

        log.info(f"Initialized Jarvis AI Engine (Ollama: {self.model_id} @ {self.host})")

    async def is_ollama_available(self) -> bool:
        """Check if local Ollama server is running."""
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.host}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def _offline_fallback_response(self, user_input: str) -> str:
        """
        Provides ultra-fast local responses for standard inquiries if Ollama server is offline.
        """
        query = user_input.lower().strip()
        now = datetime.datetime.now()

        if any(w in query for w in ["hello", "hi", "hey", "greetings"]):
            return "Hello! I am Jarvis, your AI assistant. How can I help you today?"

        if "time" in query:
            return f"It is currently {now.strftime('%I:%M %p')}."

        if "date" in query or "day" in query or "today" in query:
            return f"Today is {now.strftime('%A, %B %d, %Y')}."

        if "status" in query or "system" in query:
            return "Jarvis core systems, audio visualizer, and UI are fully operational."

        if "who are you" in query or "what is your name" in query:
            return "I am Jarvis, your next-generation desktop AI assistant."

        if "help" in query:
            return "You can ask me questions, give voice commands, or type in the prompt bar. Make sure Ollama is running for full generative AI capability."

        if "calculate" in query or re.match(r"^[\d\s\+\-\*\/\(\)\.]+$", query):
            expr = query.replace("calculate", "").strip()
            try:
                allowed_chars = set("0123456789+-*/(). ")
                if set(expr).issubset(allowed_chars):
                    res = eval(expr)
                    return f"The answer is {res}."
            except Exception:
                pass

        return (
            f"I heard: '{user_input}'. "
            f"Ollama server is currently offline. Start Ollama ('ollama run {self.model_id}') for full neural responses."
        )

    async def generate_response(self, user_input: str) -> str:
        """Helper to get the full response string quickly."""
        full_text = []
        async for chunk in self.generate_response_stream(user_input):
            full_text.append(chunk)
        return " ".join(full_text).strip()

    async def generate_response_stream(self, user_input: str):
        if not user_input or not user_input.strip():
            return

        log.info(f"Generating streaming Jarvis ({self.model_id}) response for: {user_input}")

        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p, %A, %B %d, %Y")
        system_content = f"{self.system_instruction}\nContext: The current local time is {time_str}."

        messages = [{"role": "system", "content": system_content}]
        for turn in self.conversation_history[-6:]:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["sora"]})

        messages.append({"role": "user", "content": user_input})

        full_reply = ""
        current_chunk = ""
        is_first_chunk = True
        timeout = getattr(config, "ollama_timeout", 10.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.host}/api/chat",
                    json={
                        "model": self.model_id,
                        "messages": messages,
                        "stream": True,
                        "options": {
                            "temperature": 0.4,
                            "top_p": 0.9,
                            "num_predict": 120,
                        }
                    }
                ) as response:
                    if response.status_code == 200:
                        import json
                        async for line in response.aiter_lines():
                            if not line:
                                continue
                            try:
                                data = json.loads(line)
                                token = data.get("message", {}).get("content", "")
                                if token:
                                    # Strip asterisks, hashes, backticks for clean speech
                                    clean_token = re.sub(r"[\*\_#`]", "", token)
                                    full_reply += clean_token
                                    current_chunk += clean_token

                                    # Fast yielding strategy:
                                    # Yield first chunk fast (e.g. after comma or 4 words) to minimize Time-to-First-Audio
                                    words = current_chunk.strip().split()
                                    has_sentence_end = any(current_chunk.endswith(p) for p in [". ", "? ", "! ", ".\n", "?\n", "!\n"])
                                    has_clause_break = is_first_chunk and (len(words) >= 4 and any(current_chunk.endswith(p) for p in [", ", "; ", ": "]))

                                    if has_sentence_end or has_clause_break or len(words) >= 15:
                                        piece = current_chunk.strip()
                                        if piece:
                                            yield piece
                                            current_chunk = ""
                                            is_first_chunk = False
                            except json.JSONDecodeError:
                                pass

                        if current_chunk.strip():
                            yield current_chunk.strip()

                        if full_reply.strip():
                            self._save_history(user_input, full_reply.strip())
                            log.info(f"Jarvis response complete: {full_reply.strip()}")
                        return
                    elif response.status_code == 404:
                        msg = f"Model '{self.model_id}' was not found in Ollama. Please run 'ollama pull {self.model_id}'."
                        log.warning(msg)
                        yield msg
                        return
                    else:
                        log.warning(f"Ollama returned HTTP status {response.status_code}")

        except httpx.ConnectError:
            log.warning("Could not connect to Ollama server.")
        except Exception as e:
            log.error(f"Error during Ollama inference: {e}")

        # Fallback if streaming failed
        reply = self._offline_fallback_response(user_input)
        self._save_history(user_input, reply)
        yield reply

    def _save_history(self, user_msg: str, sora_msg: str):
        self.conversation_history.append({"user": user_msg, "sora": sora_msg})
        if len(self.conversation_history) > 20:
            self.conversation_history.pop(0)
