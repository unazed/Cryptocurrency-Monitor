from random import randint
from pprint import pprint
import asyncio
import discord
import libbot
import threading


client = discord.Client()

commands = {
	"start": ("<increase|decrease|any> <percentage>", "Start the bot's monitoring"),
	"stop": (None, "Stop the bot's market watch"),
	"catch": ("<percentage> <increase|decrease>", "Set a breakpoint for when a market drops/rises a percentage"),
	"help": (None, "Displays help for commands"),
	"uncatch": (None, "Removes you from the catch list")
}
catch_users = {
	"increase": [],
	"decrease": [],
}


@client.event
async def on_message(msg):
	msg_it = msg
	msg = msg.content
	if not msg.startswith(';'):
		return
	elif msg[1:].split()[0] not in commands:
		return

	command, *arguments = msg[1:].split()

	if command == "start" and len(arguments) == 2:
		last_msg = await client.send_message(msg_it.channel, "**{*} Starting...**\n")
		for _type, change, name in run_bot(*arguments):
			new_embed = discord.Embed(title=name, description="%s **%f**" % (_type.title(), abs(change)), color=randint(0, 0xFFFFFF))
			await client.edit_message(last_msg, embed=new_embed)
			for user, _change, _ in catch_users[_type]:
				if abs(change) >= abs(_change):
					user_pm = await client.start_private_message(user)
					await client.send_message(user_pm, "The market `%s` %sd  by `%f`%% in regards to its original value." % (name, _type, abs(change)))

	elif command == "stop":
		raise SystemExit("Completed")  # ¯\_(ツ)_/¯

	elif command == "catch":
		catch_users[arguments[1]].append((msg_it.author, float(arguments[0]), msg_it.author.id)) 
		pprint(catch_users)
		return

	elif command == "uncatch":
		for _type in catch_users:
			catch_users[_type] = list(filter(lambda uid: uid[2] != msg_it.author.id, catch_users[_type]))
		pprint(catch_users)
		return

	elif command == "help":
		for k, v in commands.items():
			await client.send_message(msg_it.channel, 
				"`{}` -> `{}`\n\t`{}`".format(k, v[0], v[1]))
		return


def run_bot(high_low, perc):
	if high_low == "increase":
		high_low = False
	elif high_low == "decrease":
		high_low = True
	else:
		high_low = None
	for val in libbot.run_bot(high_low=high_low, perc=perc):
		yield val


client.run("token here)
