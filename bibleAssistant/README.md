[TODO]: https://img.shields.io/badge/TODO-0044FF?style=flat
[Done]: https://img.shields.io/badge/Done-44CC44?style=flat

# Bible Assistant
AI Assistant for analyzing biblical texts
- This is a personal project. It is designed for low-resource usage, on a personal computer, without cloud-based LLM service.
- Besides being a hobby of mine, this is an exercise in resourcefulness when you have limited resources. :-)
- Created by Yonatan Vaizman. January 2026...

---

Prep:
- This agent assumes you have downloaded bible books from Sefaria.
  - See [sefaria_code module](../sefaria/sefaria_code.py)
  - Set an environment variable (e.g., in a hidden ".env" file) SEFARIA_DATA_DIR to indicate where you want to (locally) store bible books.
  - See examples of downloading books [example_notebook](../playground/observe_bible_text.ipynb)
  - I appreciate the wonderful work of Sefaria: (https://www.sefaria.org/texts), (https://github.com/Sefaria/Sefaria-Export)
  
## This application is still under development.
Things to do:
- ![Done][Done] Agent: basic agentic framework [agent.py](agent.py)
- ![Done][Done] Interacting with the agent [talk_to_agent.ipynb](talk_to_agent.ipynb)
- ![Done][Done] Tool: lookup_verse by book, version, chapter number, verse number. [bible_tools.py](bible_tools.py)
- ![Done][Done] Generating example conversations for lookup_verse (including error in version name or book name). [generate_finetune_examples.ipynb](generate_finetune_examples.ipynb)
- ![Done][Done] Fine-tune LLM. Currently supporting Gemma3 models. LoRA. Include merge adaptation into base model, and register with local ollama. [finetune_model.ipynb](finetune_model.ipynb)
- ![TODO][TODO] Tool: search / concordance (find all biblical references for a word or phrase)
- ![TODO][TODO] Automate tool registration. Perhaps use docstrings (like in ADK) to add tool description to system-prompt and register tool's input/output schema
- ![TODO][TODO] Simplify tool schema. Make it easy on LLM (e.g., lookup_verse should accept all kinds of version names and figure out the right version). Perhaps all tools should have a dict args as single argument?
- ![TODO][TODO] Train for sequence of requests. Generate examples of consecutive requests from the user.
- ![TODO][TODO] Train for autonomous sequence of tool calls to get the answer.
- ![TODO][TODO] AgentUI: display user/assistant messages as bubbles, and display intermediate events (tool calls/responses) asynch.
- ![TODO][TODO] UI: present links to supporting evidence (I need tools to return supported evidence and AgentUI to present them nicely).
- ![TODO][TODO] Tasks: create complex examples that require a bit of planning and execusion of a sequence of function calls.
- ![TODO][TODO] Interpreting texts' meaning. Perhaps train two LLMs: One LLM to learn how/when to call tools (and a bit of planning), and second LLM to look at all the gathered text evidence and infer meaning from it (and add an "agent transfer" mechanism).
- ![TODO][TODO] Create tasks that can be verified and prepare evaluation data with designed score for the agent's result.
- ![TODO][TODO] RL: let the agent handle tasks autonomously. Examine and score the results. Re-train LLM with the higher scored paths.
- ![TODO][TODO] RLHF: once I have generative tasks (e.g., explain the meaning of the word ...; how can the word ... be interpreted in different ways...?) I can generate agent responses, human-evaluate them (or with a strong LLM as a judge), and re-train the meaning-LLM with PPO / DPO. Note: I can separate this from the goodness of the planning/executing LLM(s). I can manually craft tasks, including perfectly available evidence/quotes/references/context, and focus on the goodness of the meaning-LLM's response.
- ![TODO][TODO] Midrash. Utilize generations of interpreters of biblical text as biased-ground-truth. How can I use this (without training an LLM to think like certain old scholars/rabis)?
