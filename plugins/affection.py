
async def hold(ctx):
    target = ctx.message.content.replace('!hold ', '')
    await ctx.send(f"{ctx.author.name} holds {target}'s hand! blusH")

async def hug(ctx):
    target = ctx.message.content.replace('!hug ', '')
    await ctx.send(f"{ctx.author.name} gives {target} a hug! HyperNeko")

async def pat(ctx):
    target = ctx.message.content.replace('!pat ', '')
    await ctx.send(f"{ctx.author.name} gives {target} a pat! bongoTap")

commands = [
    ('hold', hold),
    ('hug', hug),
    ('pat', pat),
]
