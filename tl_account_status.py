import os, re, sys, time, datetime, jdatetime
import telethon
from telethon.sync import TelegramClient
from telethon.errors import (
    UserDeactivatedBanError,
    UserDeactivatedError,
    PhoneNumberBannedError,
    ChatWriteForbiddenError,
    UserIsBlockedError,
    PeerFloodError,
    FloodWaitError
)
import utility as utl


# -------------------- args --------------------
mbots_uniq_id, from_id, message_id = sys.argv[1], sys.argv[2], int(sys.argv[3])

directory = os.path.dirname(os.path.abspath(__file__))
info_msg = utl.bot.edit_message_text(
    chat_id=from_id,
    message_id=message_id,
    text="در حال بررسی ..."
)

# -------------------- db --------------------
db = utl.Database().data()
db.execute(f"SELECT * FROM {utl.mbots} WHERE uniq_id='{mbots_uniq_id}'")
row_mbots = db.fetchone()

db.execute(f"SELECT * FROM {utl.cats} WHERE id={row_mbots['cat_id']}")
row_cats = db.fetchone()

utl.get_params_pids_by_full_script_name(
    param1=row_mbots['uniq_id'],
    is_kill_proccess=True
)

# -------------------- helpers --------------------
def exit_with_message(text, status=None):
    if status is not None:
        db.execute(f"UPDATE {utl.mbots} SET status={status} WHERE id={row_mbots['id']}")
    info_msg.edit_text(text=text, parse_mode="html")
    sys.exit(0)


# -------------------- main --------------------
try:
    client = TelegramClient(
        session=f"{directory}/sessions/{row_mbots['uniq_id']}",
        api_id=row_mbots['api_id'],
        api_hash=row_mbots['api_hash']
    )
    client.connect()

    if not client.is_user_authorized():
        exit_with_message(
            text="❌ اکانت در دسترس نیست\n\n"
                 f"📞 شماره: <code>{row_mbots['phone']}</code>",
            status=0
        )

    # ---------- account health check ----------
    try:
        client(telethon.functions.account.GetAccountTTL())
        db.execute(f"UPDATE {utl.mbots} SET status=1 WHERE id={row_mbots['id']}")

    except (UserDeactivatedBanError, PhoneNumberBannedError):
        exit_with_message(
            text="⛔️ این شماره به‌صورت کامل از تلگرام مسدود شده است\n\n"
                 f"📞 شماره: <code>{row_mbots['phone']}</code>",
            status=3
        )

    except (ChatWriteForbiddenError, UserIsBlockedError):
        exit_with_message(
            text="⚠️ این اکانت محدود شده و فعلاً قابل استفاده نیست\n\n"
                 f"📞 شماره: <code>{row_mbots['phone']}</code>",
            status=2
        )

    except PeerFloodError:
        exit_with_message(
            text="🚫 اکانت به دلیل فعالیت مشکوک (Flood) موقتاً محدود شده است",
            status=2
        )

    # ---------- login code ----------
    entity = client.get_input_entity(777000)
    code, code_date = None, None

    for msg in client.iter_messages(entity, limit=5):
        if not msg.message:
            continue
        match = re.search(r"Login code: (\d+)", msg.message)
        if match:
            code = match.group(1)
            code_date = jdatetime.datetime.fromtimestamp(
                msg.date.timestamp()
            ).strftime('%Y-%m-%d %H:%M:%S')
            break

    # ---------- account info ----------
    me = client.get_me()
    password = f"<code>{row_mbots['password']}</code>" if row_mbots['password'] else "ندارد"
    code_text = f"<code>{code}</code>\n📅 {code_date}" if code else "ندارد"
    photo = "دارد" if me.photo else "ندارد"

    sessions = ""
    for s in client(telethon.functions.account.GetAuthorizationsRequest()).authorizations:
        if s.current:
            sessions += (
                f"🔻 IP: {s.ip}\n"
                f"🔻 Device: {s.device_model}\n"
                f"🔻 Platform: {s.platform}\n"
                f"🔻 App: {s.app_name} {s.app_version}\n"
                f"🔻 Active: {jdatetime.datetime.fromtimestamp(s.date_active.timestamp())}\n"
            )

    info_msg.edit_text(
        text=(
            "✅ اکانت فعال است\n\n"
            "سشن فعلی:\n"
            f"{sessions}\n"
            "اطلاعات کلی:\n"
            f"🔻 شماره: <code>{me.phone}</code>\n"
            f"🔻 نام: {me.first_name}\n"
            f"🔻 یوزرنیم: {me.username or 'ثبت نشده'}\n"
            f"🔻 تصویر: {photo}\n\n"
            f"رمز عبور: {password}\n"
            f"آخرین کد لاگین: {code_text}"
        ),
        parse_mode="html"
    )

except FloodWaitError as e:
    info_msg.edit_text(
        f"⏳ اکانت به مدت {utl.convert_time(e.seconds, 2)} محدود شده است"
    )

except Exception as e:
    print("UNEXPECTED ERROR:", repr(e))
    info_msg.edit_text("❌ خطای سیستمی\nلطفاً بعداً مجدد تلاش کنید")
