import nextcord as discord
from nextcord.ext import commands
import dotenv
import os
from stocks import stocks

dotenv.load_dotenv()

token = os.getenv("DISCORD_TOKEN")

bot = commands.Bot()

@bot.event
async def on_ready():
    print("Stocks run amok!")

@bot.slash_command(name = "shares-summary", description = "View the status of a company's shares")
async def shares(interaction: discord.Interaction, company: str = discord.SlashOption(name = "company", description = "The symbol of the company", required = True), duration: str = discord.SlashOption(name = "duration", description = "The time period over which the share prices will be shown", choices = ["1 day", "5 days", "1 month", "6 months", "Year to Date", "1 year", "5 years", "Max"], required = False)):
    if not duration:
        duration = "1 day"

    stock_data = stocks(str(interaction.user), company, duration)
    if stock_data:
        shares_embed = discord.Embed(title = f"Summary of {stock_data['name']}'s shares {stock_data['duration']}", colour = discord.Colour.blue())
        for field in list(stock_data.keys())[2:]:
            shares_embed.add_field(name = field, value = stock_data[field])

        await interaction.send(content = "***"+stock_data["name"]+"***", file = discord.File(f"shares_{interaction.user}.png"), embed = shares_embed)
    
    else:
        await interaction.send("Invalid company symbol", ephemeral = True)

bot.run(token)