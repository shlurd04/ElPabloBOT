from typing import Final
from telegram import Update, LabeledPrice, InputMediaPhoto
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN: Final = "7770334087:AAH1YRRWxZlmfWJtkAx13wl46jEedT9kYCs"
BOT_USERNAME: Final = "@elpblo_bot"
PAYMENT_PROVIDER_TOKEN: Final = '5322214758:TEST:a26a27e6-8f70-49d9-bcab-9e00a9b4e17d'
PRICE_PER_ITEM = 6000

active_orders = {}

#Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, Please place your order.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Order with : /order <Amount>')

async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    # Check if an amount was provided
    if context.args:
        try:
            # Convert the first argument to an integer (amount to order)
            amount = int(context.args[0])
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError:
            await update.message.reply_text("Please provide a valid amount (e.g., /order 3).")
            return
    else:
        await update.message.reply_text("Please specify the amount you wish to order (e.g., /order 3).")
        return

    # Check if there's an active order already
    if chat_id in active_orders:
        await update.message.reply_text("You already have an active order. Use /cancel to cancel it first.")
        return

    # Calculate the total price
    total_price = PRICE_PER_ITEM * amount
    prices = [LabeledPrice("Order Amount", total_price)]

    # Invoice details
    title = "Cocaine"
    description = f"This is an order of {amount}g of snow."
    payload = f"order-{amount}"
    currency = "GBP"

    # Store the active order
    active_orders[chat_id] = {
        "amount": amount,
        "total_price": total_price,
    }

    # Optional: Provide a photo for the invoice
    photo_url = "https://i.imgur.com/XwDhvYZ.gif"

    # Send the invoice to the user
    await context.bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency=currency,
        prices=prices,
        photo_url=photo_url,
        photo_width=256,
        photo_height=256,
        need_name=True,
        need_email=True,
        need_phone_number=True,
        need_shipping_address=True
    )

    # Inform the user about the order
    await update.message.reply_text(
        f"Your order for {amount}g of cocaine has been created with a total price of £{total_price / 100:.2f}. "
        "Please complete the payment or type /cancel to cancel the order."
    )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    # Check if the user has an active order
    if chat_id in active_orders:
        # Remove the active order
        del active_orders[chat_id]
        await update.message.reply_text("Your order has been canceled.")
    else:
        await update.message.reply_text("You don't have any active orders to cancel.")

#Handle Responses
async def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return "Hola"
    
    if 'how are you' in processed:
        return 'Estoy bien y tu?'
    
    if 'cocaine' in processed:
        return "I love snow"
    
    return "I dont know how to respond."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    response: str =  await handle_response(text)

    print('Bot: ', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} has caused the following error {context.error}')


#Main Function
if __name__ == '__main__':
    print('Bot Starting!')

    app = Application.builder().token(TOKEN).build()

    #Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('order', order_command))
    app.add_handler(CommandHandler('cancel', cancel_command))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Errors
    app.add_error_handler(error)

    #Updates
    app.run_polling(poll_interval=3)
