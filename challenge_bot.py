import os
import requests
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = -1002146260288

def get_index():
    with open("progress.txt") as f:
        return int(f.read())

def set_index(i):
    with open("progress.txt","w") as f:
        f.write(str(i))

def get_questions():
    with open("questions.txt") as f:
        return f.readlines()

def send_question(context):

    questions = get_questions()
    index = get_index()

    if index >= len(questions):
        context.bot.send_message(chat_id=GROUP_ID,text="All questions completed 🎉")
        return

    q = questions[index]

    msg = f"""
Daily HackerRank Challenge 🔥

{q}

Rules
Day 1 – Solve normally
Day 2 – Retry if both failed
After Day 2 – tools allowed
"""

    context.bot.send_message(chat_id=2146260288,text=msg)

def current(update,context):

    questions = get_questions()
    index = get_index()

    q = questions[index]

    update.message.reply_text(f"Current Question:\n{q}")

def done(update,context):

    index = get_index()
    set_index(index+1)

    update.message.reply_text("✅ Marked solved. Next question tomorrow.")

def undo(update,context):

    index = get_index()

    if index>0:
        set_index(index-1)

    update.message.reply_text("↩ Reverted to previous question")

def status(update,context):

    index = get_index()
    questions = get_questions()

    solved = index
    current_q = questions[index]

    msg=f"""
📊 Challenge Status

Questions Solved: {solved}
Current Question Number: {index+1}

Current Problem:
{current_q}
"""

    update.message.reply_text(msg)

def load(update,context):

    if len(context.args)==0:
        update.message.reply_text("Usage: /load <hackerrank_subdomain_url>")
        return

    url=context.args[0]

    headers={"User-Agent":"Mozilla/5.0"}

    response=requests.get(url,headers=headers)
    soup=BeautifulSoup(response.text,"html.parser")

    questions=[]

    for link in soup.find_all("a"):

        href=link.get("href")

        if href and "/challenges/" in href:

            title=link.text.strip()

            if title:

                full="https://www.hackerrank.com"+href
                questions.append(title+" - "+full)

    questions=list(dict.fromkeys(questions))

    with open("questions.txt","w") as f:
        for q in questions:
            f.write(q+"\n")

    set_index(0)

    update.message.reply_text(f"Loaded {len(questions)} questions.")

updater=Updater(TOKEN)

dp=updater.dispatcher

dp.add_handler(CommandHandler("current",current))
dp.add_handler(CommandHandler("done",done))
dp.add_handler(CommandHandler("undo",undo))
dp.add_handler(CommandHandler("status",status))
dp.add_handler(CommandHandler("load",load))

scheduler=BackgroundScheduler(timezone=pytz.utc)

scheduler.add_job(send_question,'cron',hour=6,minute=0,args=[updater.bot])

scheduler.start()

updater.start_polling()
updater.idle()
