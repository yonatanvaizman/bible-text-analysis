[TODO]: https://img.shields.io/badge/TODO-0044FF?style=flat
[Done]: https://img.shields.io/badge/Done-44CC44?style=flat
[WIP]: https://img.shields.io/badge/WIP-44CCCC?style=flat

# Bible Assistant
AI Assistant for analyzing biblical texts.

## Why
Learning about Biblical texts is a hobby of mine. I like listening to lectures about critical biblical research.
Sometimes, I have research questions of my own and want to do my own research and interpret the ancient text.
Here's an example scenario - when reading the story of the garden of Eden (Genesis), I wonder:
- `What's the meaning of the Hebrew word ערום (arum), said about the snake?`
- `Why is it so similar (in Hebrew) to the word ערומים (arumim), mentioned about Adam and Eve? Is it just beautiful literature, or is there a hidden meaning to it?`
- `Where else was this word ערום used and in what contexts?`
- `How did various translators choose to translate that word?`
- `What did the biblical author/editor want to teach us readers with this story?`

The biblical corpus is a convenient domain for practicing GenAI, LLM, and NLP techniques: it is public domain text, spans multiple literary genres, has many translations to other languages, is very well indexed (book, chapter, verse), and has been studied for centuries (with 200 years of modern critical researchers) - so there's plenty of resources for ground truth and evaluation.

I decided to implement an AI assistant to help me do my biblical research.
- This is a personal project. It is designed for low-resource usage, on a personal computer, without cloud-based LLM services.
- Besides being a hobby of mine, this is an exercise in resourcefulness when you have limited resources. :-)
- Created by Yonatan Vaizman. January 2026...

---

Prep:
- This agent assumes you have downloaded bible books from Sefaria.
  - See [sefaria_code module](../sefaria/sefaria_code.py)
  - Set an environment variable (e.g., in a hidden ".env" file) SEFARIA_DATA_DIR to indicate where you want to (locally) store bible books.
  - See examples of downloading books [example_notebook](../playground/observe_bible_text.ipynb)
  - I appreciate the wonderful work of Sefaria: (https://www.sefaria.org/texts), (https://github.com/Sefaria/Sefaria-Export)
- Environment:
  - Currently (Jan 2026), I am developing this repo using a personal PC with Windows 11 (personal project -> no macbook ;-) ).
  - I am using a virtual environment for python 3.12.0. (e.g., in Windows PowerShell `py -3.12 -m venv .venv`, and then `.\.venv\Scripts\activate` to enter the virtual environment).
  - Inside the "venv" install libraries `pip install -r requirements` (from the repo's main folder). It is possible that different environments need different library versions. I'll try to maintain specific [requirements.txt](../requirements.txt) for smooth reproducibility.
- Usage:
  - To "play" with this agent, go to the user entry point - [talk_to_agent.ipynb](talk_to_agent.ipynb).
  - Here's an example snapshot of a conversation with the agent (screenshot from the notebook):
  ![Example conversation with the agent](images/convo_example1.png "Example conversation with the agent")

## Project structure:
- [talk_to_agent.ipynb](talk_to_agent.ipynb): This is where I (the user) interact with the agent. At the moment, it's mainly to test if it's working properly. Hopefully, I'll get to really use the agent, ask sophisticated questions about the texts in the bible ;-).
- [agent.py](agent.py): The agentic AI framework. The frontend converses with the user, the backend communicates with a driving LLM (locally running) and calls tools.
- [bible_tools.py](bible_tools.py): Tools for the agent. If there's an efficient (and accurate) way to do something, I'll implement it programmatically with a tool.
- [test_the_tools.ipynb](test_the_tools.ipynb): A helper notebook to test/debug the functionality of the tools, regardless of any agent and LLM.
- [generate_finetune_examples.ipynb](generate_finetune_examples.ipynb): This is how I teach the LLM how to behave - what response-schema to use, when (and when not) to use tools, which tool, how to use the tools. In this notebook, I generate many example conversations that demonstrate this. Part of the challenge is covering a wide variety of scenarios (this may blow up once I add many tools, so I'll need to be careful and creative) while making sure the model's responses are "correct". Another challenge I'll have once I want the agent to start reasoning about the meaning of text (but I may dedicate a separate notebook for that ;-) ).
- [finetune_model.ipynb](finetune_model.ipynb): Taking a base model (e.g., gemma3-1b-it) and fine tuning it (using LoRA) with my custom generated examples. Then merging the adaptation parameters into the base model's parameters and registring the merged model with ollama (so that the agent can later use it to drive conversations).
- [lessons_learned.md](lessons_learned.md): This is where I take notes while researching/developing. I mark open questions that I have (or "experiments" that I want to try) and answers/lessons that I get from practice. Of course, these are not rigorous experiments and not golden conclusions, but taking these notes will help me organize.

## This application is still under development.
Things to do:
- ![Done][Done] Agent: basic agentic framework [agent.py](agent.py)
- ![Done][Done] Interacting with the agent [talk_to_agent.ipynb](talk_to_agent.ipynb)
- ![Done][Done] Tool: lookup_verse by book, version, chapter number, verse number. [bible_tools.py](bible_tools.py)
- ![Done][Done] Generating example conversations for lookup_verse (including error in version name or book name). [generate_finetune_examples.ipynb](generate_finetune_examples.ipynb)
- ![Done][Done] Fine-tune LLM. Currently supporting Gemma3 models. LoRA. Include merge adaptation into base model, and register with local ollama. [finetune_model.ipynb](finetune_model.ipynb)
- ![Done][Done] Tool: search_phrase - find all the references of verses in the bible that contain that phrase.
- ![Done][Done] Automate tool registration. Using function-signature to automatically add an option to llm response-schema. Using function doc-string to automatically add description to the system prompt.
- ![TODO][TODO] Simplify tool schema. Make it easy on LLM (e.g., lookup_verse should accept all kinds of version names and figure out the right version). Perhaps all tools should have a dict args as single argument?
- Levels of complexity of tasks:
  - ![Done][Done] Multiple available tools. Single user requests for single tool call.
  - ![Done][Done] Train for sequence of unrelated-requests (each individually prompted by the user). Generate examples of consecutive requests from the user.
  - ![TODO][TODO] Train for sequence of related-tasks to complete a bigger task. Start with single user-prompt: user giving step-by-step instructions in advance.
  - ![TODO][TODO] Train for autonomous sequence of tool calls to get the answer. User gives goal and agent plans and executes on its own.
- Agent UI:
  - ![Done][Done] UI: display user/assistant messages as bubbles.
  - ![TODO][TODO] UI: display intermediate events (tool calls/responses) asynch when they happen.
  - ![Done][Done] UI: display_convo(messages). Enable offline presentation of given messages array (for debugging, for nicely looking at synthetic training examples).
  - ![TODO][TODO] UI: present links to supporting evidence (I need tools to return supported evidence and AgentUI to present them nicely).
- ![Done][Done] Synthetic examples: try training with variations of the system prompt, to make the agent more robust and flexible for adding new tools without training. Variations have the core instructions the same, but differ in which tools are described in the "menu" and in what order.
- ![TODO][TODO] Tasks: create complex examples that require a bit of planning and execusion of a sequence of function calls.
- ![TODO][TODO] Interpreting texts' meaning. Perhaps train two LLMs: One LLM to learn how/when to call tools (and a bit of planning), and second LLM to look at all the gathered text evidence and infer meaning from it (and add an "agent transfer" mechanism).
- ![TODO][TODO] Planning/thinking: once I challenge the agent with complex tasks, should I add a capability of chain-of-thought generation - let the LLM generate a message to help it self plan (not a respond_to_user and not a tool call)? How can I integrate this into the framework - maybe a tool called "planning" or "note_to_self" with special treatment (if the LLM produces a planning message, the agent logic will immediately request the LLM for the next message)? How to avoid cycles of planning (use the response_format - regular call allows response with "planning" but after a planning response it is not immediately allowed).
- ![TODO][TODO] Create tasks that can be verified and prepare evaluation data with designed score for the agent's result.
- ![TODO][TODO] Evaluation: semi-automate evaluating using ground-truth "golden" examples. At each LLM point check if the LLM did the expected thing (call the right tool, with right args, respond correctly to user). This will be useful for training a rigid behavior, but will become less relevant once I want my agent to be autonomous and creative (once there will be many possible ways to solve a problem).
- ![TODO][TODO] Evaluation - verifiable-results: create scenarios where the end-result is verifiable, and create framework to test and judge the autonomous agent by its end result (regardless of the way to get there).
- ![TODO][TODO] RL: let the agent handle tasks autonomously. Examine and score the results. Re-train LLM with the higher scored paths.
- ![TODO][TODO] RLHF: once I have generative tasks (e.g., explain the meaning of the word ...; how can the word ... be interpreted in different ways...?) I can generate agent responses, human-evaluate them (or with a strong LLM as a judge), and re-train the meaning-LLM with PPO / DPO. Note: I can separate this from the goodness of the planning/executing LLM(s). I can manually craft tasks, including perfectly available evidence/quotes/references/context, and focus on the goodness of the meaning-LLM's response.
- ![TODO][TODO] Midrash. Utilize generations of interpreters of biblical text as biased-ground-truth. How can I use this (without training an LLM to think like certain old scholars/rabis)?
- ![TODO][TODO] Stateful / KV-cache-reuse. Once I start working with long conversations it will be slow and wasteful to send the entire conversation-so-far to ollama at every turn. I want to switch to a stateful approach, where the session remembers not only the text of the messages, but also the KV tensors. (options: vLLM, TGI, llama.cpp, implement my own tensor cache).
