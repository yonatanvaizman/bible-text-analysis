# Bible Assistant
AI Assistant for analyzing biblical texts
- This is a personal project. It is designed for low-resource usage, on a personal computer, without cloud-based LLM service.
- From constraints comes creativity :-)

Created by Yonatan Vaizman
---

This application is still under development.
## Things to do:
- [Done] Agent: basic agentic framework [agent.py](agent.py)
- [Done] Tool: lookup_verse by book, version, chapter number, verse number
- [Done] Generating example conversations for lookup_verse (including error in version name or book name)
- [Done] Fine-tune LLM. Currently supporting Gemma3 models. LoRA. Include merge adaptation into base model, and register with local ollama.
- [TODO] Tool: search / concordance (find all biblical references for a word or phrase)
- [TODO] Automate tool registration. Perhaps use docstrings (like in ADK) to add tool description to system-prompt and register tool's input/output schema
- [TODO] Simplify tool schema. Make it easy on LLM (e.g., lookup_verse should accept all kinds of version names and figure out the right version). Perhaps all tools should have a dict args as single argument?
- [TODO] Train for sequence of requests. Generate examples of consecutive requests from the user.
- [TODO] Train for autonomous sequence of tool calls to get the answer.
- [TODO] AgentUI: display user/assistant messages as bubbles, and display intermediate events (tool calls/responses) asynch.
