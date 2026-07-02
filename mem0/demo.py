import os
from openai import AzureOpenAI
from mem0 import MemoryClient
from dotenv import load_dotenv

load_dotenv()

# ── Clientes ─────────────────────────────────────────────────────────────────
mem0   = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
openai = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-08-01-preview",
)


# ── Lógica del agente ─────────────────────────────────────────────────────────
def chat(user_id: str, user_message: str) -> str:

    results = mem0.search(user_message, filters={"user_id": user_id})
    memories = results if isinstance(results, list) else results.get("results", [])

    system_prompt = (
        "Eres un asistente amigable con memoria persistente. "
        "Usa lo que recuerdas del usuario para dar respuestas personalizadas."
    )
    if memories:
        context = "\n".join(f"- {m['memory']}" for m in memories)
        system_prompt += f"\n\nLo que recuerdas del usuario:\n{context}"

    # 3. Llamar al LLM
    completion = openai.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
    )
    assistant_message = completion.choices[0].message.content

    # 4. Guardar conversación en mem0 Platform
    mem0.add(
        [
            {"role": "user",      "content": user_message},
            {"role": "assistant", "content": assistant_message},
        ],
        user_id=user_id,
    )

    return assistant_message


# ── Loop de consola ───────────────────────────────────────────────────────────
def main():
    print("=" * 54)
    print("   Mem0 Platform Demo — Agente con memoria en la nube")
    print("=" * 54)
    print("Comandos: 'memoria' para ver recuerdos | 'salir' para salir\n")

    user_id = input("¿Cuál es tu nombre? ").strip() or "usuario"
    print(f"\nHola {user_id}! Recuerdo todo lo que me cuentes entre sesiones.\n")

    while True:
        try:
            user_input = input(f"{user_id}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n¡Hasta luego!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("salir", "exit", "quit"):
            print("¡Hasta luego!")
            break

        if user_input.lower() == "memoria":
            all_mem = mem0.get_all(filters={"user_id": user_id})
            items = all_mem if isinstance(all_mem, list) else all_mem.get("results", [])
            if items:
                print("\n[Tus memorias guardadas]")
                for i, m in enumerate(items, 1):
                    print(f"  {i}. {m['memory']}")
            else:
                print("[Aún no tienes memorias guardadas]")
            print()
            continue

        response = chat(user_id, user_input)
        print(f"\nAsistente: {response}\n")


if __name__ == "__main__":
    main()
