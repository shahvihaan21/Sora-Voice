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
        self.model_id = config.ollama_model or "qwen3:1.7b"
        self.conversation_history: List[Dict[str, str]] = []
        self._client: httpx.AsyncClient | None = None
        self._clean_trans = str.maketrans("", "", "*_#`")

        self.system_instruction = (
            "You are Jarvis, a lightning-fast, ultra-smart, elegant, and friendly AI desktop assistant. "
            "You provide concise, highly accurate, and conversational answers. "
            "Speak naturally without markdown formatting, bullet symbols, or robotic phrasing. "
            "Keep voice responses crisp, direct, and under 2-3 sentences unless detailed explanation is requested."
        )

        log.info(f"Initialized Jarvis AI Engine (Ollama: {self.model_id} @ {self.host})")

    def _get_client(self) -> httpx.AsyncClient:
        # Persistent client with appropriate timeouts for local models
        timeout_val = getattr(config, "ollama_timeout", 30.0)
        try:
            if self._client is None or self._client.is_closed:
                timeout_config = httpx.Timeout(timeout_val, connect=5.0, read=timeout_val, write=10.0)
                self._client = httpx.AsyncClient(timeout=timeout_config)
        except Exception:
            return httpx.AsyncClient(timeout=timeout_val)
        return self._client

    async def close(self):
        """Cleanly close persistent HTTP client on shutdown."""
        if self._client and not self._client.is_closed:
            try:
                await self._client.aclose()
            except Exception:
                pass
            self._client = None

    async def prewarm(self):
        try:
            client = self._get_client()
            await client.get(f"{self.host}/api/tags", timeout=2.5)
        except Exception:
            pass

    async def is_ollama_available(self) -> bool:
        """Check if local Ollama server is running."""
        try:
            client = self._get_client()
            res = await client.get(f"{self.host}/api/tags", timeout=2.0)
            return res.status_code == 200
        except Exception:
            return False

    async def get_available_models(self) -> List[str]:
        """Discover installed models dynamically through the Ollama API."""
        try:
            client = self._get_client()
            res = await client.get(f"{self.host}/api/tags", timeout=3.0)
            if res.status_code == 200:
                data = res.json()
                models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                return models
        except Exception as e:
            log.debug(f"Could not discover Ollama models: {e}")
        return []

    async def validate_model(self, model_name: str) -> bool:
        """Validate if the selected model is present in Ollama."""
        available = await self.get_available_models()
        if not available:
            return False
        # Allow exact match or match without tag if applicable
        return model_name in available or any(m.startswith(f"{model_name}:") for m in available)

    def set_model(self, model_name: str):
        """Switch active Ollama model without restart."""
        self.model_id = model_name
        config.ollama_model = model_name
        log.info(f"Switched active Ollama model to: {self.model_id}")

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

        target_model = self.model_id
        # Route to vision model only when user explicitly asks for image/screenshot understanding
        is_vision_query = any(k in user_input.lower() for k in ["screenshot", "look at my screen", "read screen", "describe screen", "image analysis"])
        target_model = getattr(config, "vision_model", "qwen2.5vl:7b") if is_vision_query else self.model_id

        log.info(f"Generating streaming Jarvis ({target_model}) response for: {user_input}")

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
        has_yielded = False
        timeout = getattr(config, "ollama_timeout", 30.0)

        try:
            client = self._get_client()
            async with client.stream(
                "POST",
                f"{self.host}/api/chat",
                json={
                    "model": target_model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": 0.4,
                        "top_p": 0.9,
                        "num_predict": 120,
                    }
                },
                timeout=timeout
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
                                clean_token = token.translate(self._clean_trans)
                                full_reply += clean_token
                                current_chunk += clean_token
                                words = len(current_chunk.split())
                                stripped_chunk = current_chunk.rstrip()

                                # Fast yielding strategy for minimum TTFA (Time-To-First-Audio):
                                has_sentence_end = any(stripped_chunk.endswith(p) for p in (".", "?", "!"))
                                has_clause_break = is_first_chunk and words >= 3 and any(stripped_chunk.endswith(p) for p in (",", ";", ":"))

                                if (has_sentence_end and words >= 1) or has_clause_break or words >= 12:
                                    piece = current_chunk.strip()
                                    if piece:
                                        has_yielded = True
                                        yield piece
                                        current_chunk = ""
                                        is_first_chunk = False
                        except json.JSONDecodeError:
                            pass

                    if current_chunk.strip():
                        has_yielded = True
                        yield current_chunk.strip()

                    if full_reply.strip():
                        self._save_history(user_input, full_reply.strip())
                        log.info(f"Jarvis response complete: {full_reply.strip()}")
                    return
                elif response.status_code == 404:
                    msg = f"Model '{target_model}' was not found in Ollama. Please run 'ollama pull {target_model}'."
                    log.warning(msg)
                    yield msg
                    return
                else:
                    log.warning(f"Ollama returned HTTP status {response.status_code}")
        except httpx.ConnectError:
            log.warning("Could not connect to Ollama server.")
        except httpx.TimeoutException:
            log.warning(f"Ollama inference timed out after {timeout}s.")
            timeout_msg = f"Ollama inference timed out after {int(timeout)}s. Local model '{target_model}' took too long to respond."
            self._save_history(user_input, timeout_msg)
            yield timeout_msg
            return
        except Exception as e:
            log.error(f"Error during Ollama inference: {e}")

        # Fallback if streaming failed and no chunks were produced
        if not has_yielded:
            reply = self._offline_fallback_response(user_input)
            self._save_history(user_input, reply)
            yield reply

    def _save_history(self, user_msg: str, sora_msg: str):
        self.conversation_history.append({"user": user_msg, "sora": sora_msg})
        if len(self.conversation_history) > 20:
            self.conversation_history.pop(0)
