import discord
import random
import json
import aiosqlite
from discord.ext import commands




bot = commands.Bot(command_prefix='$')







@bot.command()
async def purchase(ctx):
    embed = discord.Embed(title="Payment Information", description=" ADD INFO", color=0xeee657)
    embed.add_field(name="PAYMENT PROCESSOR", value="DETAILS", inline=False)

    await ctx.author.send(embed=embed)
    await ctx.send(embed=embed)


@bot.command()
async def update(ctx, amount, user: discord.Member=None):
    if ctx.author.id != "OWNERS DISCORD ID":
        await ctx.send("You do not have access to this command")
        return
    amount = int(amount)
    db = await aiosqlite.connect("botDB.sqlite")
    cursor = await db.cursor()
    await cursor.execute("""
    UPDATE balance SET coins = (coins + ?) WHERE userid = ?
    """, (amount, user.id))
    await db.commit()
    await db.close()
    await ctx.author.send(f"{user.mention} balance has been incremented by {amount}!")

@bot.event
async def on_ready():
    with open("botDB.sqlite","a+") as f:
        pass
    db = await aiosqlite.connect("botDB.sqlite")
    cursor = await db.cursor()
    await cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS "cards" (
        "number"    TEXT,
        "ccv"       INTEGER,
        "zip"       INTEGER,
        "exp"       TEXT,
        PRIMARY KEY("number")
        );
    """)
    await db.commit()
    await cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS "balance" (
        "userid"    INTEGER,
        "coins"    INTEGER DEFAULT 0,
        PRIMARY KEY("userid")
        );
    """)
    await db.commit()
    await db.close()

    print("Bot is ready")
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


# add card to sql
@bot.command()
async def add_card(ctx, ccv, zip, exp, *, number):
    db = await aiosqlite.connect("botDB.sqlite")
    cursor = await db.cursor()
    await cursor.execute("""
    INSERT OR IGNORE INTO cards (ccv, zip, exp, number) VALUES(?, ?, ?, ?)
    """, (ccv, zip, exp, number))
    await db.commit()
    await db.close()
    await ctx.send("Card has been added")



@bot.command()
async def balance(ctx):
    db = await aiosqlite.connect("botDB.sqlite")
    cursor = await db.cursor()
    await cursor.execute("""
    INSERT OR IGNORE INTO balance (userid) VALUES(?)
    """, (ctx.author.id,))
    await cursor.execute("""
    SELECT coins FROM balance WHERE userid = ?
    """, (ctx.author.id,))
    balance = await cursor.fetchone()
    balance = balance[0]
    await db.commit()
    await db.close()
    await ctx.send(f"{ctx.author.mention} balance is {balance}")
    await ctx.author.send(f"{ctx.author.mention} balance is {balance}")

#test - creates a random cc value
@bot.command()
async def test(ctx):
    db = await aiosqlite.connect("botDB.sqlite")
    cursor = await db.cursor()
    await cursor.execute("""
        INSERT OR IGNORE INTO cards (ccv, zip, exp, number) VALUES(034, 11385, '02/12', '2039 2939 4859 8377')
        """)
    await db.commit()
    await db.close()
    await ctx.author.send("Random Card info has been added")

# generates a VCC
@bot.command()
async def generate(ctx):
    db = await aiosqlite.connect("botDB.sqlite")
    cursor = await db.cursor()
    await cursor.execute("""
     SELECT coins FROM balance WHERE userid = ?
    """, (ctx.author.id,))
    balance = await cursor.fetchone()
    balance = balance[0]
    if balance<1:
        await ctx.send("Balance is insufficient to generate. $purchase to reup")
        return
    else:
        # check if there are any vccs available in CARDS
        await cursor.execute("""
        SELECT number, ccv, zip, exp  FROM cards 
        """)
        card = await cursor.fetchone()

        if card is None:
            await ctx.send("No cards available.")
            return
        number = card[0]
        ccv = card[1]
        zip = card[2]
        exp = card[3]

        # attempt to send card info to dm
        try:
            embed = discord.Embed(title="VCC", description="Card Info: ", color=0xeee657)

            embed.add_field(name="Card Number: ", value=number)

            embed.add_field(name="CVV: ", value=zip)

            embed.add_field(name="EXP: ", value=ccv)

            embed.add_field(name="Zip Code: ", value=exp)

            await ctx.send(embed=embed)
            await ctx.author.send(embed=embed)

            # remove card from sql
            await cursor.execute("""
            DELETE FROM cards WHERE number = ?
            """, (number,))

            # update balance: coins = coins - 1
            await cursor.execute("""
                UPDATE balance SET coins = (coins - 1) WHERE userid = ?
                """, (ctx.author.id,))



        except discord.HTTPException:
            generalch = bot.get_channel(MESSAGE ID)
            await generalch.send(
                f"{ctx.author.mention} you do not allow pms from non friends :( this messages is to inform you that your your card was not securely sent to your dms")
    await db.commit()
    await db.close()




# removes default help
bot.remove_command('help')

#help command
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="{NAME} BOT", description="Commands: ", color=0xeee657)


    #generate
    embed.add_field(name="$generate", value="Creates unique CODES", inline=False)

    #balance
    embed.add_field(name="$balance", value="Coins available", inline=False)


    #purchase
    embed.add_field(name="$purchase", value="Payment details", inline=False)


    # $update (amount) (@user)
    # $add_card ccv zip exp cc#

    await ctx.send(embed=embed)


bot.run('INSERT TOKEN HERE')
