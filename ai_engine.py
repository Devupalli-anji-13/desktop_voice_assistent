
import requests

from config import (
    KIE_API_KEY,
    KIE_API_ENDPOINT,
    KIE_MODEL_NAME,
    SYSTEM_INSTRUCTIONS
)


def ask_jarvis(question, selected_model=None, history=None):

    if not KIE_API_KEY:
        raise ValueError("KIE_API_KEY is missing from .env")

    if not question or not question.strip():
        return "Please ask me a question."

    headers = {
        "Authorization": f"Bearer {KIE_API_KEY}",
        "Content-Type": "application/json"
    }

    conversation = []

    if history:
        for message in history:
            role = message.get("role")
            content = message.get("content")

            if role in ("user", "assistant") and content:
                conversation.append({
                    "role": role,
                    "content": [{
                        "type": (
                            "input_text" if role == "user"
                            else "output_text"
                        ),
                        "text": str(content)
                    }]
                })

    conversation.append({
        "role": "user",
        "content": [{
            "type": "input_text",
            "text": question.strip()
        }]
    })

    payload = {
        "model": KIE_MODEL_NAME,
        "stream": False,
        "instructions": SYSTEM_INSTRUCTIONS,
        "input": conversation,
        "reasoning": {"effort": "high"}
    }

    try:
        response = requests.post(
            KIE_API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=120
        )

        response.raise_for_status()
        data = response.json()

        if data.get("code") or data.get("error"):
            raise RuntimeError(
                data.get("msg") or str(data.get("error"))
            )

        parts = []

        for item in data.get("output", []):
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        parts.append(content.get("text", ""))

        answer = "\n".join(
            part for part in parts if part
        ).strip()

        if not answer:
            raise RuntimeError("The KIE API returned no answer.")

        return answer

    except requests.exceptions.Timeout:
        raise RuntimeError("KIE request timed out.")

    except requests.exceptions.ConnectionError:
        raise RuntimeError("Cannot connect to KIE.ai.")

    except requests.exceptions.HTTPError as error:
        try:
            details = response.json()
        except ValueError:
            details = response.text

        raise RuntimeError(
            f"KIE HTTP error: {error}\n{details}"
        )

    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"KIE request failed: {error}")
