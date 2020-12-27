
async def hello(ctx):
    await ctx.send('Hi!!')

commands = [
    ('hello', hello)
]
