#!/usr/bin/env python

import razorpay
import config
import datetime as dt
from addict import Dict
from dateutil.relativedelta import relativedelta
from utils import setup_logger
import re

# setup loggers
info_logger = setup_logger("rp_auto_info_logger", "./logs/rp_automate.info.log")
error_logger = setup_logger(
    "rp_auto_error_logger", "./logs/rp_automate.error.log", "ERROR"
)

# setup for_date
for_date = (
    dt.datetime.today()
    if config.MASS_INTENTION_FOR_DATE.lower() == "today"
    else dt.datetime.strptime(config.MASS_INTENTION_FOR_DATE, "%d %b %Y")
)

info_logger.info("Initialzed RP Automate")
info_logger.info(f"Fetching Intentions for {for_date.strftime('%-d-%b-%Y')}")

try:
    client = razorpay.Client(auth=(config.API_KEY, config.API_SECRET))

    # fetch all payments
    from_date_timestamp = int(
        (for_date - relativedelta(months=config.FETCH_PAYMENTS_UPTO or 12)).timestamp()
    )
    payments = Dict()
    last_fetched_timestamp = for_date.timestamp()

    info_logger.info(
        f"Setup Client, Fetching payments from {dt.datetime.fromtimestamp(from_date_timestamp).strftime('%-d-%b-%Y')} to {for_date.strftime('%-d-%b-%Y')}"
    )

    while last_fetched_timestamp > from_date_timestamp:
        payments_resp = Dict(client.payment.all({"count": 100, "skip": len(payments)}))

        if payments_resp.count <= 0:
            break

        payments_fetched_count = payments_resp.count
        payments += payments_resp["items"]
        last_fetched_timestamp = int(payments_resp["items"][-1].created_at)

except Exception as err:
    error_logger.exception(err)
    raise

info_logger.info(f"Fetched {len(payments)} Payments")

# filter out captured payments only
payments = [item for item in payments if item.status == "captured"]

# filter out todays mass offerings
mass_intentions = []
for payment in payments:
    try:
        if (
            payment.notes
            and dt.datetime.strptime(payment.notes.date_for_the_mass, "%d %b %Y").date()
            == for_date.date()
        ):
            mass_intentions.append(
                Dict(
                    {
                        key: val
                        for key, val in payment.notes.items()
                        if key not in ["phone", "email", "date_for_the_mass"]
                    }
                )
            )

    except:
        continue

info_logger.info(
    f"Found {len(mass_intentions)} Mass Intentions for {for_date.strftime('%-d-%b-%Y')}"
)

# Try to filter by time
import datefinder

message_context = Dict()
for data in mass_intentions:

    if not data.time_of_the_mass_to_be_offered_for:
        if not message_context[config.DEFAULT_MASS_TIME]:
            message_context[config.DEFAULT_MASS_TIME] = []
        message_context[config.DEFAULT_MASS_TIME].append(data)
        continue

    guess_time = list(
        datefinder.find_dates(
            re.sub(
                r"(.*\d)( *[/./,/;/:] *|)(\d\d)",
                r"\1:\3",
                data.time_of_the_mass_to_be_offered_for,
            )
        )
    )
    if not guess_time:
        if not message_context.Unknown:
            message_context.Unknown = []
        message_context.Unknown.append(data)
        continue

    guess_time = guess_time[0].strftime("%-I:%M")
    if not message_context[guess_time]:
        message_context[guess_time] = []

    message_context[guess_time].append(data)


# Draft response Whatsapp Message
info_logger.info("Drafting Whatsapp Message")

wa_message = f"*Mass Intentions for _{for_date.strftime('%B %-d, %Y')}._*\n"
for time, values in message_context.items():
    if time == "Unknown" or not values:
        continue

    # default = " Default" if time == config.DEFAULT_MASS_TIME else ""
    wa_message += f"\n*Offerings for _{time.strip()}_ Mass:* \n"

    for value in values:
        wa_message += f"\n_{value.mass_intention.strip()}_\nMass offered by *{value.mass_offered_by.strip()}*\n"

if message_context.Unknown:
    wa_message += "\n*Other Mass Intentions:*\n"

    for value in message_context.Unknown:
        wa_message += f"\nTime of Mass: *{value.time_of_the_mass_to_be_offered_for.strip()}*\n_{value.mass_intention.strip()}_\nMass offered by *{value.mass_offered_by.strip()}*\n"

if not message_context.values():
    wa_message += "\nNo Mass Intentions.\n"

# Check count
if len(mass_intentions) != sum([len(val) for val in message_context.values()]):
    wa_message += "\nCOUNT MISMATCH ERROR, Check RazorPay!\n"
    error_logger.error("Intentions Count Mismatch!")
info_logger.info("Verified Count")

info_logger.info(f"\n{wa_message}")
# print(wa_message)  # For debugging purposes only

# Init WhatappAPI & Send the message
info_logger.info("Sending Whatsapp Message")
from wa_api import WhatsappAPI

try:
    whatsapp = WhatsappAPI(wa_profile=config.SENDER_WHATSAPP_PROFILE)

    receiver = None
    if "RECEIVERS_GROUP_NAME" in dir(config) and config.RECEIVERS_GROUP_NAME:
        groups = Dict(
            {
                group.id: {group.name: group.id}
                for group in whatsapp.driver.get_all_groups()
            }
        )

        if config.RECEIVERS_GROUP_NAME in [list(v.keys())[0] for v in groups.values()]:
            for val in groups.values():
                if list(val.keys())[0] == config.RECEIVERS_GROUP_NAME:
                    receiver = val[config.RECEIVERS_GROUP_NAME]
        else:
            error_logger.error(
                f"No Group Found with the name {config.RECEIVERS_GROUP_NAME}"
            )

    if "RECEIVERS_NUMBER" in dir(config) and config.RECEIVERS_NUMBER:
        receiver = config.RECEIVERS_NUMBER

    if whatsapp.send_message(wa_message, receiver):
        info_logger.info("Whatsapp Message Sent")
    whatsapp.quit()

except Exception as err:
    error_logger.exception(err)
    raise

info_logger.info("RP Automate Session Ended")
