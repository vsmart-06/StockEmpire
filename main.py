import nextcord as discord
from nextcord.ext import commands
import dotenv
import os
from stocks import stocks, getTrending, getWinners, getLosers, getCrypto
from records import add_ticker, remove_ticker, get_portfolio, delete_portfolio, isCompany

dotenv.load_dotenv()

token = os.getenv("DISCORD_TOKEN")

bot = commands.Bot()

@bot.event
async def on_ready():
    print("Stocks run amok!")
    await bot.change_presence(activity = discord.Game("Stocks run amok!"))

@bot.slash_command(name = "ticker", description = "View the status of a company's shares")
async def ticker(interaction: discord.Interaction, company: str = discord.SlashOption(name = "company", description = "The symbol of the company", required = True), duration: str = discord.SlashOption(name = "duration", description = "The time period over which the share prices will be shown", choices = ["1 day", "5 days", "1 month", "6 months", "Year to Date", "1 year", "5 years", "Max"], required = False)):
    if not duration:
        duration = "1 day"
    company = company.lower()
    if isCompany(company):
        await interaction.response.defer()
        stock_data = stocks(str(interaction.user), company, duration)
        shares_embed = discord.Embed(title = f"Summary of {stock_data['name']}'s shares {stock_data['duration']}", colour = discord.Colour.blue())
        for field in list(stock_data.keys())[2:]:
            shares_embed.add_field(name = field, value = stock_data[field])

        shares_embed.set_footer(text = f"Source: https://finance.yahoo.com/quote/{company.upper()}?p={company.upper()}")

        view = discord.ui.View(timeout = 120)
        async def timeout():
            new_view = discord.ui.View(timeout = None)
            for x in view.children:
                button = x
                button.disabled = True
                new_view.add_item(button)
            await interaction.edit_original_message(view = new_view)
        view.on_timeout = timeout

        buttons = []
        durations = ["1 day", "5 days", "1 month", "6 months", "Year to Date", "1 year", "5 years", "Max"]
        for x in durations:
            button = discord.ui.Button(label = x, style = discord.ButtonStyle.blurple)
            if duration == x:
                button.disabled = True
            buttons.append(button)
        
        def create_callback(duration):
            async def callback(btn_interaction: discord.Interaction):
                if btn_interaction.user != interaction.user:
                    await btn_interaction.send("This is not for you!", ephemeral = True)
                    return
                new_buttons = []
                for x in durations:
                    button = discord.ui.Button(label = x, style = discord.ButtonStyle.blurple)
                    if duration == x:
                        button.disabled = True
                    new_buttons.append(button)
                new_buttons[0].callback = create_callback("1 day")
                new_buttons[1].callback = create_callback("5 days")
                new_buttons[2].callback = create_callback("1 month")
                new_buttons[3].callback = create_callback("6 months")
                new_buttons[4].callback = create_callback("Year to Date")
                new_buttons[5].callback = create_callback("1 year")
                new_buttons[6].callback = create_callback("5 years")
                new_buttons[7].callback = create_callback("Max")
                new_view = discord.ui.View(timeout = 120)
                new_view.on_timeout = timeout
                for x in new_buttons:
                    new_view.add_item(x)

                new_stock_data = stocks(str(btn_interaction.user), company, duration)
                new_shares_embed = discord.Embed(title = f"Summary of {new_stock_data['name']}'s shares {new_stock_data['duration']}", colour = discord.Colour.blue())
                for field in list(new_stock_data.keys())[2:]:
                    new_shares_embed.add_field(name = field, value = new_stock_data[field])

                new_shares_embed.set_footer(text = f"Source: https://finance.yahoo.com/quote/{company.upper()}?p={company.upper()}")

                await btn_interaction.edit(file = discord.File(f"shares_{btn_interaction.user}_{company}.png"), embed = new_shares_embed, view = new_view)

            return callback
        
        buttons[0].callback = create_callback("1 day")
        buttons[1].callback = create_callback("5 days")
        buttons[2].callback = create_callback("1 month")
        buttons[3].callback = create_callback("6 months")
        buttons[4].callback = create_callback("Year to Date")
        buttons[5].callback = create_callback("1 year")
        buttons[6].callback = create_callback("5 years")
        buttons[7].callback = create_callback("Max")

        for x in buttons:
            view.add_item(x)


        await interaction.send(content = "***"+stock_data["name"]+"***", file = discord.File(f"shares_{interaction.user}_{company}.png"), embed = shares_embed, view = view)
    
    else:
        await interaction.send("Invalid company symbol", ephemeral = True)

@bot.slash_command(name = "portfolio", description = "View, add, or remove tickers from your portfolio")
async def portfolio(interaction: discord.Interaction):
    pass

@portfolio.subcommand(name = "view", description = "View your portfolio")
async def portfolio_view(interaction: discord.Interaction):
    user_portfolio = get_portfolio(interaction.user.id)
    if user_portfolio:
        await interaction.response.defer()
        shares_embeds = []
        for x in range(len(user_portfolio)):
            company: str = user_portfolio[x]
            stock_data = stocks(str(interaction.user), company)
            shares_embed = discord.Embed(title = stock_data["name"], colour = discord.Colour.blue())
            shares_embed.add_field(name = "Symbol", value = company.upper(), inline = False)
            shares_embed.add_field(name = "Last Price", value = stock_data["Last Price"])
            shares_embed.add_field(name = "Change", value = stock_data["Change"])
            shares_embed.add_field(name = "Percentage Change", value = stock_data["Percentage Change"])

            shares_embed.set_footer(text = f"Source: https://finance.yahoo.com/quote/{company.upper()}?p={company.upper()}")
            shares_embeds.append(shares_embed)

        view = discord.ui.View(timeout = 120)

        async def timeout():
            new_view = discord.ui.View(timeout = None)
            for x in view.children:
                button = x
                button.disabled = True
                new_view.add_item(button)
            await interaction.edit_original_message(view = new_view)

        view.on_timeout = timeout

        def create_callback(company: str):
            async def callback(btn_interaction: discord.Interaction):
                if btn_interaction.user != interaction.user:
                    await btn_interaction.send("This is not for you!", ephemeral = True)
                    return
                new_view = discord.ui.View(timeout = 120)
                new_view.on_timeout = timeout
                new_buttons = []
                for x in user_portfolio:
                    new_buttons.append(discord.ui.Button(label = x.upper(), style = discord.ButtonStyle.blurple))
                new_buttons[0].callback = create_callback(new_buttons[0].label.lower())
                if user_portfolio.index(company) == 0:
                    new_buttons[0].disabled = True
                new_view.add_item(new_buttons[0])
                if len(new_buttons) >= 2:
                    new_buttons[1].callback = create_callback(new_buttons[1].label.lower())
                    if user_portfolio.index(company) == 1:
                        new_buttons[1].disabled = True
                    new_view.add_item(new_buttons[1])
                if len(new_buttons) >= 3:
                    new_buttons[2].callback = create_callback(new_buttons[2].label.lower())
                    if user_portfolio.index(company) == 2:
                        new_buttons[2].disabled = True
                    new_view.add_item(new_buttons[2])
                if len(new_buttons) >= 4:
                    new_buttons[3].callback = create_callback(new_buttons[3].label.lower())
                    if user_portfolio.index(company) == 3:
                        new_buttons[3].disabled = True
                    new_view.add_item(new_buttons[3])
                if len(new_buttons) >= 5:
                    new_buttons[4].callback = create_callback(new_buttons[4].label.lower())
                    if user_portfolio.index(company) == 4:
                        new_buttons[4].disabled = True
                    new_view.add_item(new_buttons[4])
                stock_data = stocks(str(btn_interaction.user), company)
                shares_embed = discord.Embed(title = f"Summary of {stock_data['name']}'s shares {stock_data['duration']}", colour = discord.Colour.blue())
                for field in list(stock_data.keys())[2:]:
                    shares_embed.add_field(name = field, value = stock_data[field])
                shares_embed.set_footer(text = f"Source: https://finance.yahoo.com/quote/{company.upper()}?p={company.upper()}")
                await btn_interaction.edit(content = "***"+stock_data["name"]+"***", file = discord.File(f"shares_{btn_interaction.user}_{company}.png"), embed = shares_embed, view = new_view)
            
            return callback

        buttons = []
        for x in user_portfolio:
            buttons.append(discord.ui.Button(label = x.upper(), style = discord.ButtonStyle.blurple))
        
        buttons[0].callback = create_callback(buttons[0].label.lower())
        view.add_item(buttons[0])
        if len(buttons) >= 2:
            buttons[1].callback = create_callback(buttons[1].label.lower())
            view.add_item(buttons[1])
        if len(buttons) >= 3:
            buttons[2].callback = create_callback(buttons[2].label.lower())
            view.add_item(buttons[2])
        if len(buttons) >= 4:
            buttons[3].callback = create_callback(buttons[3].label.lower())
            view.add_item(buttons[3])
        if len(buttons) >= 5:
            buttons[4].callback = create_callback(buttons[4].label.lower())
            view.add_item(buttons[4])

        await interaction.send("***Your portfolio***", embeds = shares_embeds, view = view)

    else:
        await interaction.send("You have not created a portfolio yet!", ephemeral = True)

@portfolio.subcommand(name = "add", description = "Add a ticker to your portfolio")
async def portfolio_add(interaction: discord.Interaction, company: str = discord.SlashOption(name = "company", description = "The symbol of the company you would like to add to your portfolio", required = True)):
    await interaction.response.defer(ephemeral = True)
    company = company.lower()
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
async def portfolio_remove(interaction: discord.Interaction, company: str = discord.SlashOption(name = "company", description = "The symbol of the company you would like to remove from your portfolio", required = True)):
    await interaction.response.defer(ephemeral = True)
    company = company.lower()
    result = remove_ticker(interaction.user.id, company)
    if result == 0:
        await interaction.send("Invalid company symbol", ephemeral = True)
    elif result == 1:
        await interaction.send("This company is not there in your portfolio!", ephemeral = True)
    elif result == 2:
        await interaction.send("You have not created a portfolio yet!", ephemeral = True)
    else:
        await interaction.send("Ticker removed!", ephemeral = True)

@portfolio.subcommand(name = "delete", description = "Delete your portfolio")
async def portfolio_delete(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral = True)
    if delete_portfolio(interaction.user.id):
        await interaction.send("Portfolio deleted!", ephemeral = True)
    else:
        await interaction.send("You do not have a portfolio to delete!", ephemeral = True)

@bot.slash_command(name = "trending", description = "Get the trending stocks")
async def trending(interaction: discord.Interaction):
    await interaction.response.defer()
    trending_stocks = getTrending()
    shares_embeds = []
    for x in range(len(trending_stocks)):
        company: str = trending_stocks[x]
        stock_data = stocks(str(interaction.user), company)
        shares_embed = discord.Embed(title = stock_data["name"], colour = discord.Colour.blue())
        shares_embed.add_field(name = "Symbol", value = company.upper(), inline = False)
        shares_embed.add_field(name = "Last Price", value = stock_data["Last Price"])
        shares_embed.add_field(name = "Change", value = stock_data["Change"])
        shares_embed.add_field(name = "Percentage Change", value = stock_data["Percentage Change"])

        shares_embed.set_footer(text = f"Source: https://finance.yahoo.com/quote/{company.upper()}?p={company.upper()}")
        shares_embeds.append(shares_embed)

    view = discord.ui.View(timeout = 120)

    async def timeout():
        new_view = discord.ui.View(timeout = None)
        for x in view.children:
            button = x
            button.disabled = True
            new_view.add_item(button)
        await interaction.edit_original_message(view = new_view)

    view.on_timeout = timeout

    def create_callback(company: str):
        async def callback(btn_interaction: discord.Interaction):
            if btn_interaction.user != interaction.user:
                await btn_interaction.send("This is not for you!", ephemeral = True)
                return
            new_view = discord.ui.View(timeout = 120)
            new_view.on_timeout = timeout
            new_buttons = []
            for x in trending_stocks:
                new_buttons.append(discord.ui.Button(label = x.upper(), style = discord.ButtonStyle.blurple))
            new_buttons[0].callback = create_callback(new_buttons[0].label.lower())
            if trending_stocks.index(company) == 0:
                new_buttons[0].disabled = True
            new_view.add_item(new_buttons[0])
            if len(new_buttons) >= 2:
                new_buttons[1].callback = create_callback(new_buttons[1].label.lower())
                if trending_stocks.index(company) == 1:
                    new_buttons[1].disabled = True
                new_view.add_item(new_buttons[1])
            if len(new_buttons) >= 3:
                new_buttons[2].callback = create_callback(new_buttons[2].label.lower())
                if trending_stocks.index(company) == 2:
                    new_buttons[2].disabled = True
                new_view.add_item(new_buttons[2])
            if len(new_buttons) >= 4:
                new_buttons[3].callback = create_callback(new_buttons[3].label.lower())
                if trending_stocks.index(company) == 3:
                    new_buttons[3].disabled = True
                new_view.add_item(new_buttons[3])
            if len(new_buttons) >= 5:
                new_buttons[4].callback = create_callback(new_buttons[4].label.lower())
                if trending_stocks.index(company) == 4:
                    new_buttons[4].disabled = True
                new_view.add_item(new_buttons[4])
            stock_data = stocks(str(btn_interaction.user), company)
            shares_embed = discord.Embed(title = f"Summary of {stock_data['name']}'s shares {stock_data['duration']}", colour = discord.Colour.blue())
            for field in list(stock_data.keys())[2:]:
                shares_embed.add_field(name = field, value = stock_data[field])
            shares_embed.set_footer(text = f"Source: https://finance.yahoo.com/quote/{company.upper()}?p={company.upper()}")
            await btn_interaction.edit(content = "***"+stock_data["name"]+"***", file = discord.File(f"shares_{btn_interaction.user}_{company}.png"), embed = shares_embed, view = new_view)
        
        return callback

    buttons = []
    for x in trending_stocks:
        buttons.append(discord.ui.Button(label = x.upper(), style = discord.ButtonStyle.blurple))
    
    buttons[0].callback = create_callback(buttons[0].label.lower())
    view.add_item(buttons[0])
    if len(buttons) >= 2:
        buttons[1].callback = create_callback(buttons[1].label.lower())
        view.add_item(buttons[1])
    if len(buttons) >= 3:
        buttons[2].callback = create_callback(buttons[2].label.lower())
        view.add_item(buttons[2])
    if len(buttons) >= 4:
        buttons[3].callback = create_callback(buttons[3].label.lower())
        view.add_item(buttons[3])
    if len(buttons) >= 5:
        buttons[4].callback = create_callback(buttons[4].label.lower())
        view.add_item(buttons[4])

    await interaction.send("***Trending Stocks***", embeds = shares_embeds, view = view)

@bot.slash_command(name = "todays", description = "View today's winners/losers")
async def days(interaction: discord.Interaction):
    pass

@days.subcommand(name = "winners", description = "View today's winners")
async def winners(interaction: discord.Interaction):
    getWinners()

@days.subcommand(name = "losers", description = "View today's losers")
async def losers(interaction: discord.Interaction):
    getLosers()

@bot.slash_command(name = "crypto", description = "View the highest valued cryptocurrency stocks")
async def crypto(interaction: discord.Interaction):
    getCrypto()

bot.run(token)