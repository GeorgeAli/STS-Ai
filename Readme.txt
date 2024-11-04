The program begins by initializing a coordinator and a SimpleAgent within STS_AI.py.

Coordinator: The coordinator facilitates communication between the agent and the Communication Mod. This functionality is implemented in communication/coordinator.py. 
Additionally, the Action.py file within the same directory enables the agent to create "actions" – JSON-encoded messages sent to stdout, where they are accessed by the Communication Mod for in-game execution.

Spire Directory: This directory contains essential classes and structures for managing game data. Within it, card_dictionary.py holds a complete set of Ironclad cards for gameplay reference.

AI Directory: The AI directory houses agent.py and priorities.py, which form the core of the AI’s decision-making process. priorities.py includes configurable weights for map 
directions and card preferences, contributing to effective deck-building and navigation strategies.