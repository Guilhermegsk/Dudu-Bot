import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup
import json

URL_SITE = 'https://portais.ufma.br/PortalUfma/paginas/restaurante.jsf'


def obter_cardapio():
    response = requests.get(URL_SITE)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tabela = soup.find('table')  
        tbody = tabela.find('tbody')

        cardapio = {}
        for tr in tbody.find_all('tr'):
            th = tr.find('th') 
            tds = tr.find_all('td')
            if th and len(tds) == 2:
                item = th.text.strip()
                almoco = tds[0].text.strip()
                jantar = tds[1].text.strip()
                cardapio[item] = {'almoco': almoco, 'jantar': jantar}

        with open('cardapio.json', 'w', encoding='utf-8') as f:
            json.dump(cardapio, f, ensure_ascii=False, indent=4)
        return cardapio
    else:
        return None


intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot {bot.user} está pronto e comandos de barra sincronizados!")

#
class MenuCommand(app_commands.Group):
    """Grupo de comandos para exibir o cardápio do restaurante universitário."""

    @app_commands.command(name="almoco", description="Exibe o cardápio do almoço.")
    async def almoco(self, interaction: discord.Interaction):
        cardapio = obter_cardapio()
        if not cardapio:
            await interaction.response.send_message("Erro ao obter o cardápio. Tente novamente mais tarde.", ephemeral=True)
            return

        mensagem = "**Cardápio do Almoço**\n"
        for item, valores in cardapio.items():
            if "Detalhar almoço" in valores['almoco']:
                continue
            mensagem += f"**{item}**: {valores['almoco']}\n"

        await interaction.response.send_message(mensagem)

    @app_commands.command(name="jantar", description="Exibe o cardápio do jantar.")
    async def jantar(self, interaction: discord.Interaction):
        cardapio = obter_cardapio()
        if not cardapio:
            await interaction.response.send_message("Erro ao obter o cardápio. Tente novamente mais tarde.", ephemeral=True)
            return

        mensagem = "**Cardápio do Jantar**\n"
        for item, valores in cardapio.items():
            if "Detalhar jantar" in valores['jantar']:
                continue
            mensagem += f"**{item}**: {valores['jantar']}\n"

        await interaction.response.send_message(mensagem)


bot.tree.add_command(MenuCommand(name="menu"))


bot.run(BOT_TOKEN)