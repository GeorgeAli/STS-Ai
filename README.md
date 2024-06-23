# Slaying the Spire
# Hunter College CSCI 49900 Capstone Project

This project is built using ForgottenArbiter's spirecomm which communicates with Slay the Spire through his Communication Mod.

Goals: improvements of existing ai based on certain categories like clear rate, and speed by using Minimax algorithm.

Website : https://slayingthespire.netlify.app/aicomparison.html


# SetUp :
1. Install three mods
   * Install [Communication Mod](https://github.com/ForgottenArbiter/CommunicationMod)
   * ModTheSpire - Steam Workshop version
   * BaseMod - Steam Workshop version
2. Update Communication Mod config
  * Windows: `%LOCALAPPDATA%\ModTheSpire\CommunicationMod\config.properties` 
  * Linux: `~/.config/ModTheSpire/config.properties` 
  * Mac: `~/Library/Preferences/ModTheSpire/config.properties` 
3. Set command=python3 Location where is the main.py
  * e.g) `command=python3 path_to_script/main.py`
4. Launch Slay The Spire with mods and go to communication mods setting and click "Start External Process"


If the mod does not run correctly
* check the `communication_mod_errors.log`
You can find it Steam->select "Slay the Spire" -> click "Manage"-> "Browse localfile"->"Resource"


[Presentation Link - Has more diagrams and info](https://docs.google.com/presentation/d/1RxQuOPTGZf5BejvV4l8MaKA3IbAYYN19-rI9gjpSf4s/edit#slide=id.p)
