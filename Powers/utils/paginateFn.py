import importlib
from pyrogram import enums, filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from AnonXMusic import HELP_COMMANDS, app
from AnonXMusic.utils.kbhelpers import ikb

module_num = 24


# Function to convert text to small caps styled font
def to_styled_font(text):
    normal = "abcdefghijklmnopqrstuvwxyz"  # Normal alphabet
    small_caps = "abcdefghijklmnopqrstuvwxyz"  # Corresponding small caps
    translation_table = str.maketrans(normal, small_caps)  # Create translation table
    text = text.capitalize()  # Capitalize the first letter of the text
    return text[0] + text[1:].translate(translation_table)  # Apply translation to the rest

# Function to paginate the help modules and create inline keyboard markup
def paginate_modules(page, module_dict, prefix):
    modules = sorted(module_dict.keys())  # Sort module names alphabetically
    # Split modules into pages of 12 items each
    pairs = [modules[i * module_num:(i + 1) * module_num] for i in range((len(modules) + module_num - 1) // module_num)]
    max_num_pages = len(pairs)  # Total number of pages
    modulo_page = page % max_num_pages  # Handle page overflow by looping back
    mod_pairs = pairs[modulo_page]  # Get modules for the current page
    # Create a button for each module, storing its name and the current page number
    mod_buttons = [InlineKeyboardButton(mod, callback_data=f"{prefix}module({module_dict[mod]}|{modulo_page})") for mod in mod_pairs]

    # Arrange buttons in rows of 3
    buttons = [mod_buttons[i:i + 3] for i in range(0, len(mod_buttons), 3)]

    # If there are multiple pages, add navigation buttons
    if len(pairs) > 1:
        buttons.append([
            InlineKeyboardButton("◀️", callback_data=f"{prefix}prev({modulo_page - 1})"),  # Previous page button
            InlineKeyboardButton("Home", callback_data="settingsback_helper"),  # Home button
            InlineKeyboardButton("▶️", callback_data=f"{prefix}next({modulo_page + 1})")  # Next page button
        ])
    else:
        buttons.append([InlineKeyboardButton("Home", callback_data="settingsback_helper")])  # Only Home button if single page
    
    return InlineKeyboardMarkup(buttons)  # Return the keyboard layout

# Function to generate help buttons for the main help menu
def generate_help_buttons(page=0):
    modules = {}
    # Iterate over each item in HELP_COMMANDS to prepare the help menu
    for plugin_name, plugin_data in HELP_COMMANDS.items():
        try:
            name = to_styled_font(plugin_name.split(".")[1])  # Extract and style the module name
            modules[name] = plugin_name  # Store in modules dictionary
        except AttributeError:
            continue  # Skip if there's an error extracting the name
    return paginate_modules(page, modules, prefix="help_")  # Paginate and return the buttons

# Callback query handler for help navigation and module display
@app.on_callback_query(filters.regex(r"help_(module|prev|next|back)\((.+)\)"))
async def module_help(client: Client, query: CallbackQuery):
    action, data = query.data.split("(")[0].split("_")[1], query.data.split("(")[1].split(")")[0]

    if action == "module":
        module_name, page = data.split("|")  # Split module name and page number
        module_data = HELP_COMMANDS.get(module_name, {})  # Get module help data
        help_msg = module_data.get("help_msg", "No help available for this module.")
        module_buttons = module_data.get("buttons", [])

        # Create a back button with the current page number
        reply_markup = ikb(module_buttons, True, todo=f"settings_back_helper({page})")

        try:
            await query.edit_message_text(
                text=help_msg,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        except MediaCaptionTooLong:
            await client.send_message(chat_id=query.message.chat.id, text=help_msg)
            await query.answer()      
        except Exception as e:
            await query.answer("Error: " + str(e), show_alert=True)
        return

    elif action in ["prev", "next"]:
        page = int(data)
        help_buttons = generate_help_buttons(page=page)
        await query.message.edit_reply_markup(reply_markup=help_buttons)

    elif action == "back":
        page = int(data)  # Retrieve the page number from callback data
        help_buttons = generate_help_buttons(page=page)  # Generate buttons for that page
        await query.message.edit_reply_markup(reply_markup=help_buttons)

    await query.answer()
