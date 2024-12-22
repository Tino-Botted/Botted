from discord import activity, app_commands
import asyncio
import discord
from discord.app_commands import Group
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import Greedy, Context
from discord.ui import Button, View
from typing import Literal, Optional
from discord import app_commands
import json
from datetime import datetime

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
start_date_pretty = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="-", intents=intents, application_id=1286032438547582997)
    
    async def setup_hook(self):
        await self.tree.sync()
    
    async def on_ready(self):
        print("Bot is ready.")

class DropdownSettings(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Ephermal Messages (Only visible to you)", value="ephermal_message"),
            discord.SelectOption(label="Examples", value="definitionexamples")
        ]
        super().__init__(placeholder="Choose a setting...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]

        with open('usersettings.json', 'r') as file:
            json_settings = (json.load(file))

        ephermal_messages = json_settings[0]["users"][0][str(interaction.user.id)][0]["ephermal_message"]

        if ephermal_messages == "True":
            ephermal_messages2 = "On."
        else:
            ephermal_messages2 = "Off."

        examples = json_settings[0]["users"][0][str(interaction.user.id)][0]["examples"]

        if examples == "True":
            examples = "On."
        else:
            examples = "Off."


        if selected_value == "definitionexamples":
            option = "Examples"
        elif selected_value == "ephermal_message":
            option = "Ephermal Messages (only visible to you messages)"

        select = EphermalMessages()
        view = discord.ui.View()
        view.add_item(select)

        if ephermal_messages2 == "On.":
            on_off_color = discord.Color.green()
        else:
            on_off_color = discord.Color.red()

        if examples == "On.":
            on_off_color = discord.Color.green()
        else:
            on_off_color = discord.Color.red()

        embed=discord.Embed(title="Ephermal Messages (only visible to you messages)", description=f"{option} are currently set to {ephermal_messages2}", color=on_off_color)
        await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
       
class EphermalMessages(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.green)
    async def ephermal_messages_on(self, interaction: discord.Interaction):
        with open('usersettings.json', 'r') as file:
            json_settings = (json.load(file))

        json_settings[0]["users"][0][str(interaction.user.id)][0]["ephermal_message"] = selected_value

        with open('usersettings.json', 'w') as file:
            json.dump(json_settings, file, indent=4)
        
        interaction.response.send_message(f"Successfully turned Ephermal Messages (Only visible to you messages) to {selected_value}")
    
    @discord.ui.button(label="Enable", style=discord.ButtonStyle.red)
    async def ephermal_messages_off(self, interaction: discord.Interaction):
        with open('usersettings.json', 'r') as file:
            json_settings = (json.load(file))

        json_settings[0]["users"][0][str(interaction.user.id)][0]["ephermal_message"] = selected_value

        with open('usersettings.json', 'w') as file:
            json.dump(json_settings, file, indent=4)
        
        interaction.response.send_message(f"Successfully turned Ephermal Messages (Only visible to you messages) to {selected_value}")

class DictionaryButtons(discord.ui.View):
    def __init__(self, word):
        self.savedword = word
        super().__init__()

    @discord.ui.button(label="More Definitions", style=discord.ButtonStyle.primary)
    async def moredefinitions_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        word = self.savedword
        print(word)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}") as response:
                html = await response.json()

                worddata = html[:11]
                
        newlist = []
        definitions = []
        synonymslist = []
        antonymslist = []

        for only_definitions in worddata[0]["meanings"][0]["definitions"]:
            newlist.append(only_definitions['definition'])    
            print(newlist)

        for index, definition in enumerate(newlist):
            definitions.append(f"{index}. {definition}")

        if worddata[0]["meanings"][0]["definitions"][0]["synonyms"] == []:
            synonymslist.append("There are no synonyms for this word.")
        else:
            for synonyms in worddata[0]["meanings"][0]["definitions"][0]["synonyms"]:
                synonymslist.append(synonyms)

        if worddata[0]["meanings"][0]["definitions"][0]["synonyms"] == []:
            antonymslist.append("There are no antonyms for this word.")
        else:
            for antonyms in worddata[0]["meanings"][0]["definitions"][0]["antonyms"]:
                antonymslist.append(antonyms)

        definition_and_synonyms = '\n'.join(definitions)
        embed = discord.Embed(title=f"""{word} - More Definitions""", description=f"""{definition_and_synonyms}""")
        await interaction.followup.send(embed=embed)

    @discord.ui.button(label="Settings", style=discord.ButtonStyle.primary)
    async def settings_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        select = DropdownSettings()
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message("Choose one of the avaible settings:", ephemeral=True, view=view)

@bot.tree.command(name="dictionary", description="Define a Word and more using https://dictionaryapi.dev/")
@app_commands.describe(word="Which word do you want to know more about?")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
async def dictionarycommand(interaction: discord.Interaction, word: str):
    await interaction.response.defer()
    try:
        if " " not in word:
            button_class = DictionaryButtons(word)
            button_class.saveword = word
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}") as response:
                    html = await response.json()
                    worddata = html[:11]

            phoneticslist = []
            synonymslist = []
            antonymslist = []
            if worddata[0]["phonetics"][0]["text"] == []: 
                phoneticslist.append("There are no phonetics for this word.")
            else: 
                for getphonetics in worddata[0]["phonetic"][0]["text"]:
                    phoneticslist.append(getphonetics)

            if worddata[0]["meanings"][0]["definitions"][0]["synonyms"] == []:
                synonymslist.append("There are no synonyms for this word.")
            else:
                for synonyms in worddata[0]["meanings"][0]["definitions"][0]["synonyms"]:
                    synonymslist.append(synonyms)

            if worddata[0]["meanings"][0]["definitions"][0]["synonyms"] == []:
                antonymslist.append("There are no antonyms for this word.")
            else:
                for antonyms in worddata[0]["meanings"][0]["definitions"][0]["antonyms"]:
                    antonymslist.append(antonyms)

            embed = discord.Embed(title=f""""{worddata[0]["word"]}" - Dictionary""", description=f"Definition: \n{worddata[0]["meanings"][0]["definitions"][0]["definition"]} \n\nsynonyms: {', '.join(synonymslist)} \nantonyms: {', '.join(antonymslist)} \nphonetics: {', '.join(phoneticslist)} \nPart of Speech: {worddata[0]["meanings"][0]["partOfSpeech"]}", color=discord.Color.blue())
            await interaction.followup.send(embed=embed, view=DictionaryButtons(word))
        else: await interaction.response.send_message(f"""Do not use spaces in the option "word". You have entered: "{word}" """)
    except Exception as e:
        error_embed = discord.Embed(title=f""""{word}" - Error""", description=f"An Error occured while trying to find that word. There can be multiple reasons for this. Here are some:\n - The Word might not be in the dictionary, so the word can't be found. Make sure you entered the word without special characters and that it is an english word. \n - The API didn't respond. maybe the api im using doesn't respond and just gives a 404 Error. This doesn't usually happen, but you can check for yourself by going to https://api.dictionaryapi.dev/api/v2/entries/en/{word} but if it shows you can try again. \n - It is possbile that you're maybe trying to execute the command while I am testing stuff. Try again in a few hours or tomorrow.")
        error_embed.add_field(name="", value="If you think that is not the case, please ask for help in my server (<https://discord.gg/hzzCSPKbmV>)")
        await interaction.followup.send(embed=error_embed)
        print(e)

bot.run("")