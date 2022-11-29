import nextcord as discord
from nextcord.ext import commands
import dotenv
import os
from stocks import stocks
from records import add_ticker, remove_ticker, get_portfolio

dotenv.load_dotenv()

token = os.getenv("DISCORD_TOKEN")

bot = commands.Bot()

@bot.event
async def on_ready():
    print("Stocks run amok!")

@bot.slash_command(name = "ticker", description = "View the status of a company's shares")
async def ticker(interaction: discord.Interaction, company: str = discord.SlashOption(name = "company", description = "The symbol of the company", required = True), duration: str = discord.SlashOption(name = "duration", description = "The time period over which the share prices will be shown", choices = ["1 day", "5 days", "1 month", "6 months", "Year to Date", "1 year", "5 years", "Max"], required = False)):
    if not duration:
        duration = "1 day"

    stock_data = stocks(str(interaction.user), company, duration)
    if stock_data:
        shares_embed = discord.Embed(title = f"Summary of {stock_data['name']}'s shares {stock_data['duration']}", colour = discord.Colour.blue())
        for field in list(stock_data.keys())[2:]:
            shares_embed.add_field(name = field, value = stock_data[field])

        shares_embed.set_footer(text = f"Source: https://finance.yahoo.com/quote/{company.upper()}?p={company.upper()}")

        await interaction.send(content = "***"+stock_data["name"]+"***", file = discord.File(f"shares_{interaction.user}.png"), embed = shares_embed)
    
    else:
        await interaction.send("Invalid company symbol", ephemeral = True)

@bot.slash_command(name = "portfolio", description = "View, add, or remove tickers from your portfolio")
async def portfolio(interaction: discord.Interaction):
    pass

@portfolio.subcommand(name = "view", description = "View your portfolio")
async def portfolio_view(interaction: discord.Interaction):
    user_portfolio = get_portfolio(interaction.user.id)
    if user_portfolio:
        for x in range(len(user_portfolio)):
            company = user_portfolio[x]
            stock_data = stocks(str(interaction.user), company)
            shares_embed = discord.Embed(title = f"Summary of {stock_data['name']}'s shares {stock_data['duration']}", colour = discord.Colour.blue())
            for field in list(stock_data.keys())[2:]:
                shares_embed.add_field(name = field, value = stock_data[field])

            shares_embed.set_footer(text = f"Source: https://finance.yahoo.com/quote/{company.upper()}?p={company.upper()}")

            await interaction.send(content = "***"+stock_data["name"]+"***", file = discord.File(f"shares_{interaction.user}.png"), embed = shares_embed)

    else:
        await interaction.send("You have not created a portfolio yet!", ephemeral = True)

@portfolio.subcommand(name = "add", description = "Add a ticker to your portfolio")
async def portfolio_view(interaction: discord.Interaction, company: str = discord.SlashOption(name = "company", description = "The symbol of the company you would like to add to your portfolio", required = True)):
    result = add_ticker(interaction.user.id, company)
    if result == 0:
        await interaction.send("Invalid company symbol", ephemeral = True)
    elif result == 1:
        await interaction.send("You can't add more than 5 companies to your portfolio!", ephemeral = True)
    elif result == 2:
        await interaction.send("This company is already in your portfolio!", ephemeral = True)
    else:
        await interaction.send("Ticker added!", ephemeral = True)


@portfolio.subcommand(name = "remove", description = "Remove a ticker from your portfolio")
async def portfolio_view(interaction: discord.Interaction, company: str = discord.SlashOption(name = "company", description = "The symbol of the company you would like to remove from your portfolio", required = True)):
    result = remove_ticker(interaction.user.id, company)
    if result == 0:
        await interaction.send("Invalid company symbol", ephemeral = True)
    elif result == 1:
        await interaction.send("This company is not there in your portfolio!", ephemeral = True)
    elif result == 2:
        await interaction.send("You have not created a portfolio yet!", ephemeral = True)
    else:
        await interaction.send("Ticker removed!", ephemeral = True)

bot.run(token)