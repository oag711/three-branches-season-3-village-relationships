# Days at Three Branches agent

Edit `agent.py` to give every one of your villagers a routine. The platform runs a separate `Agent` instance for each NPC, so instances do not share variables or memory. The supplied `sandbox/` directory contains the local runner, types, and village helpers. Leave it unchanged, and leave `requirements.in` and `requirements.txt` alone: the pinned packages match the server.

Start with the [Getting Started guide](https://vox-deorum.github.io/game-sandbox/students/getting-started/). Then run these commands from this folder:

```console
python -m sandbox watch  # watch your villagers and the scripted visitor
python -m sandbox test   # run the checks
python -m sandbox eval   # run repeatable automated days
```

## Files you will use

| Path | Purpose |
| --- | --- |
| `agent.py` | Your `Agent` implementation and starter TODOs. |
| `environment.md` | Rules, helpers, observations, and local commands. |
| `manifest.json` | Tells Game Sandbox where the agent class lives. |
| `season.json` | Optional local season settings downloaded from My Submissions. |
| `tests/` | Checks your submission should pass. |
| `sandbox/` | Local game, helpers, and types. Do not edit it. |
| `requirements.txt` | Exact Python package versions used by the server. |
| `requirements-dev.txt` | Test dependencies. |
| `.env.example` | Example local LLM settings. |

The starter shows `action.walk`, `action.stand`, an emote, and `use`. Read [`environment.md`](environment.md) before changing it. Begin with one behavior that you can recognize in `watch`, then make it more responsive to the people and props it sees.

Chat is optional. If you add `chat(self, inbox)` to your agent, send and receive raw message dictionaries that use canonical player IDs such as `"player_0"` and `"player_1"`. For example, return `[{"to": "player_0", "text": "Hello."}]` to send a direct message. The village helpers do not include a chat namespace. Read [`environment.md`](environment.md#chat-with-other-agents) for the inbox format, broadcasts, and delivery timing.

In `watch` and `eval`, your `Agent` controls the whole cast, and `scripted_visitor` controls the visitor. The `naive` built-in is the simple baseline for the cast. When you are ready to submit, follow the [submitting guide](https://vox-deorum.github.io/game-sandbox/students/submitting/).

## Optional LLM API

If your instructor enables model calls, follow [Using the LLM API](llm.md). Copy `.env.example` to `.env`, add the endpoint and key, and never commit either secret.

Test the connection with:

```console
python -m sandbox llm
```

Design Goal

My goal for Season 3 is to make the village feel more alive by giving villagers different jobs and routines while allowing them to acknowledge other characters. Each villager has an assigned role and a destination, and villagers wave when they see someone. I want these behaviors to make the villagers feel like individuals who share the same village rather than characters that all behave identically.

Design Reflection

For my agent, I chose to assign each villager a role based on its player number. Some villagers travel to the pump, benches, crops, or crates, while others wander between available destinations or return toward their home doorway. This gives the village a variety of activities instead of having every villager follow the same routine. I used breadth-first search (BFS) to find reachable cells and build routes through the village. The agent checks which cells it can safely enter and follows the resulting route toward its destination. This approach helps villagers navigate around obstacles instead of simply walking directly toward a target. I also added route tracking so that a villager can continue following its route between decisions.

Another behavior I added is waving when someone is visible. The agent uses the people.seen(observation) function to decide whether to use the "wave" expression. This provides a simple way for villagers to acknowledge other characters. Villagers assigned to benches can also use a nearby bench when it is available. One tradeoff is that each villager follows a relatively simple routine. Although the roles create variety, the villagers do not have a complete relationship system or conversations with one another. Their waving behavior is also based on whether someone is visible, rather than on a specific friendship or relationship. The route system can help with navigation, but villagers may still pause or encounter difficulties when moving around other characters.

Compared with my earlier approach, I focused on making movement more organized by using reachable cells and route tracking. I also wanted the villagers' behavior to be easier to understand by giving each one a specific responsibility. If I had more time, I would improve how villagers respond to one another, make their movement look more natural, and develop more meaningful interactions that show relationships between characters.

AI-Use Reflection

I used ChatGPT to help me understand and improve my Python agent. I asked for help with route tracking, waving behavior, and organizing my code. Using AI helped me understand possible changes to my agent and identify areas where its movement and behavior could be improved. However, suggestions did not always solve the pauses I observed during gameplay, which helped me recognize that changing the agent may not fix every issue in the simulation. I reviewed the suggested code in relation to my existing implementation and used gameplay observations to evaluate its behavior. This experience showed me that AI can be useful for troubleshooting and explaining code, but I still need to test the results and make sure the implementation matches the assignment requirements.