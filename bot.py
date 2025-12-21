import os, re, time, shutil, requests, zipfile, datetime, jdatetime, telegram, telegram.ext, utility as utl


directory = os.path.dirname(os.path.abspath(__file__))
filename = str(os.path.basename(__file__))

utl.get_params_pids_by_full_script_name(script_names=[f"{directory}/{filename}"], is_kill_proccess=True)
print(f"ok: {filename}")


if not os.path.exists(f"{directory}/sessions"):
    os.mkdir(f"{directory}/sessions")
if not os.path.exists(f"{directory}/import"):
    os.mkdir(f"{directory}/import")
if not os.path.exists(f"{directory}/export"):
    os.mkdir(f"{directory}/export")
if not os.path.exists(f"{directory}/files"):
    os.mkdir(f"{directory}/files")


def user_panel(message, text=None, reply_to_message_id=None):
    if not text:
        text = "ناحیه کاربری:"
    message.reply_html(
        text=text,
        reply_to_message_id=reply_to_message_id,
        reply_markup={'resize_keyboard': True,'keyboard': [
            [{'text': "📋 سفارش ها"}, {'text': "➕ ایجاد سفارش"}],
            [{'text': "📋 اکانت ها"}, {'text': "➕ افزودن اکانت"}],
            [{'text': "‏📋 API ها"}, {'text': "➕ افزودن API"}],
            [{'text': "📋 دسته بندی ها"}, {'text': "➕ ایجاد دسته بندی"}],
            [{'text': "👤 کاربر"}, {'text': "🔮 آنالیز"}, {'text': "⚙️ تنظیمات"}],
            [{'text': "📣 کانال کش"}]
        ]}
    )


def callbackquery_process(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    bot = context.bot
    query = update.callback_query
    message = query.message
    message_id = message.message_id
    from_id = query.from_user.id
    chat_id = message.chat.id
    data = query.data
    ex_data = data.split(';')
    timestamp = int(time.time())

    if data == "test":
        return
    if data == "nazan":
        return query.answer("Do not touch 😕")
    
    cs = utl.Database()
    cs = cs.data()

    cs.execute(f"SELECT * FROM {utl.admin}")
    row_admin = cs.fetchone()
    cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={from_id}")
    row_user = cs.fetchone()
    
    if from_id in utl.admins or row_user['status'] == 1:
        if ex_data[0] == 'pg':
            if ex_data[1] == 'accounts':
                selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                i = selected_pages + 1
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE user_id IS NOT NULL ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                result = cs.fetchall()
                if not result:
                    return query.answer(text="⛔️ صفحه دیگری وجود ندارد", show_alert=True)
                
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL")
                rowcount = cs.fetchone()['count']
                output = f"📜 لیست همه اکانت ها ({rowcount:,})\n\n"
                for row in result:
                    cs.execute(f"SELECT * FROM {utl.cats} WHERE id={row['cat_id']}")
                    row_cats = cs.fetchone()
                    if row['status'] == 2:
                        output += f"{i}. شماره: <code>{row['phone']}</code>\n"
                        output += f"⛔ محدودیت: ({utl.convert_time((row['end_restrict'] - timestamp),2)})\n"
                    else:
                        output += f"{i}. شماره: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                    output += f"📂 دسته بندی: ‏/category_{row['id']} ‏({row_cats['name']})\n"
                    output += f"🔸️ وضعیت: /status_{row['id']}\n"
                    output += f"❌ حذف: /delete_{row['id']}\n\n"
                    i += 1
                ob = utl.Pagination(update, "accounts", output, utl.step_page, rowcount)
                return ob.process()
            if ex_data[1] == '0':
                selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                i = selected_pages + 1
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE status=0 AND user_id IS NOT NULL ORDER BY last_order_at DESC LIMIT {selected_pages},{utl.step_page}")
                result = cs.fetchall()
                if not result:
                    return query.answer(text="⛔️ صفحه دیگری وجود ندارد", show_alert=True)
                
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status=0 AND user_id IS NOT NULL")
                rowcount = cs.fetchone()['count']
                output = f"📜 لیست اکانت های لاگ اوت شده ({rowcount:,})\n\n"
                for row in result:
                    cs.execute(f"SELECT * FROM {utl.cats} WHERE id={row['cat_id']}")
                    row_cats = cs.fetchone()
                    output += f"{i}. شماره: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                    output += f"📂 دسته بندی: ‏/category_{row['id']} ‏({row_cats['name']})\n"
                    output += f"🔸️ وضعیت: /status_{row['id']}\n"
                    output += f"❌ حذف: /delete_{row['id']}\n\n"
                    i += 1
                ob = utl.Pagination(update, "0", output, utl.step_page, rowcount)
                return ob.process()
            if ex_data[1] == '1':
                selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                i = selected_pages + 1
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE status=1 ORDER BY last_order_at ASC LIMIT {selected_pages},{utl.step_page}")
                result = cs.fetchall()
                if not result:
                    return query.answer(text="⛔️ صفحه دیگری وجود ندارد", show_alert=True)
                
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status=1 AND user_id IS NOT NULL")
                rowcount = cs.fetchone()['count']
                output = f"📜 لیست اکانت های فعال ({rowcount:,})\n\n"
                for row in result:
                    cs.execute(f"SELECT * FROM {utl.cats} WHERE id={row['cat_id']}")
                    row_cats = cs.fetchone()
                    output += f"{i}. شماره: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                    output += f"📂 دسته بندی: ‏/category_{row['id']} ‏({row_cats['name']})\n"
                    output += f"🔸️ وضعیت: /status_{row['id']}\n"
                    output += f"❌ حذف: /delete_{row['id']}\n\n"
                    i += 1
                ob = utl.Pagination(update, "1", output, utl.step_page, rowcount)
                return ob.process()
            if ex_data[1] == '2':
                selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                i = selected_pages + 1
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE status=2 ORDER BY end_restrict ASC LIMIT {selected_pages},{utl.step_page}")
                result = cs.fetchall()
                if not result:
                    return query.answer(text="⛔️ صفحه دیگری وجود ندارد", show_alert=True)
                
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status=2 AND user_id IS NOT NULL")
                rowcount = cs.fetchone()['count']
                output = f"📜 لیست اکانت های محدود شده ({rowcount:,})\n\n"
                for row in result:
                    cs.execute(f"SELECT * FROM {utl.cats} WHERE id={row['cat_id']}")
                    row_cats = cs.fetchone()
                    output += f"{i}. شماره: <code>{row['phone']}</code>\n"
                    output += f"⛔ محدودیت: ({utl.convert_time((row['end_restrict'] - timestamp),2)})\n"
                    output += f"📂 دسته بندی: ‏/category_{row['id']} ‏({row_cats['name']})\n"
                    output += f"🔸️ وضعیت: /status_{row['id']}\n"
                    output += f"❌ حذف: /delete_{row['id']}\n\n"
                    i += 1
                ob = utl.Pagination(update, "2", output, utl.step_page, rowcount)
                return ob.process()
            if ex_data[1] == 'orders':
                selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                i = selected_pages + 1
                cs.execute(f"SELECT * FROM {utl.orders} WHERE status>0 ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                result = cs.fetchall()
                if not result:
                    return query.answer(text="⛔️ صفحه دیگری وجود ندارد", show_alert=True)
                
                now = jdatetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=3, minutes=30)))
                time_today = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
                time_yesterday = time_today - 86400
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.orders}")
                count = cs.fetchone()['count']
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.orders} WHERE created_at>={time_today}")
                orders_count_today = cs.fetchone()['count']
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.orders} WHERE created_at<{time_today} AND created_at>={time_yesterday}")
                orders_count_yesterday = cs.fetchone()['count']

                cs.execute(f"SELECT sum(count_done) FROM {utl.orders} WHERE status=2")
                orders_count_moved_all = cs.fetchone()['sum(count_done)']
                orders_count_moved_all = orders_count_moved_all if orders_count_moved_all is not None else 0
                cs.execute(f"SELECT sum(count_done) FROM {utl.orders} WHERE status=2 AND created_at>={time_today}")
                orders_count_moved_today = cs.fetchone()['sum(count_done)']
                orders_count_moved_today = orders_count_moved_today if orders_count_moved_today is not None else 0
                cs.execute(f"SELECT sum(count_done) FROM {utl.orders} WHERE status=2 AND created_at<{time_today} AND created_at>={time_yesterday}")
                orders_count_moved_yesterday = cs.fetchone()['sum(count_done)']
                orders_count_moved_yesterday = orders_count_moved_yesterday if orders_count_moved_yesterday is not None else 0

                output = f"📋 کل سفارش ها: {count} ({orders_count_moved_all})\n"
                output += f"🟢 سفارش های امروز: {orders_count_today} ({orders_count_moved_today})\n"
                output += f"⚪️ سفارش های دیروز: {orders_count_yesterday} ({orders_count_moved_yesterday})\n\n"
                for row in result:
                    group_link = f"<a href='{row['group_link']}'>{row['group_link'].replace('https://t.me/', '')}</a>" if row['group_link'] is not None else "با فایل انجام شده"
                    output += f"{i}. جزییات: /order_{row['id']}\n"
                    output += f"🔹️ گروه: {group_link}\n"
                    output += f"🔹️ انجام شده / درخواستی: [{row['count_done']} / {row['count']}]\n"
                    output += f"🔹️ وضعیت: {utl.status_orders[row['status']]}\n"
                    output += f"📅️ ایجاد: {jdatetime.datetime.fromtimestamp(row['created_at']).astimezone(datetime.timezone(datetime.timedelta(hours=3, minutes=30))).strftime('%Y/%m/%d %H:%M')}\n\n"
                    i += 1
                ob = utl.Pagination(update, "orders", output, utl.step_page, count)
                return ob.process()
            if ex_data[1] == 'categories':
                selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                i = selected_pages + 1
                cs.execute(f"SELECT * FROM {utl.cats} ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                result = cs.fetchall()
                if not result:
                    return query.answer(text="⛔️ صفحه دیگری وجود ندارد", show_alert=True)
                
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.cats}")
                rowcount = cs.fetchone()['count']
                output = f"📋 دسته بندی ها ({rowcount})\n\n"
                for row in result:
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE cat_id={row['id']}")
                    count_mbots = cs.fetchone()['count']
                    output += f"{i}. ‏{row['name']} ‏({count_mbots} اکانت)\n"
                    output += f"❌ حذف: /DeleteCat_{row['id']}\n\n"
                    i += 1
                ob = utl.Pagination(update, "categories", output, utl.step_page, rowcount)
                return ob.process()
            if ex_data[1] == 'apis':
                selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                i = selected_pages + 1
                cs.execute(f"SELECT * FROM {utl.apis} ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                result = cs.fetchall()
                if not result:
                    return query.answer(text="⛔️ صفحه دیگری وجود ندارد", show_alert=True)
                
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.apis}")
                rowcount = cs.fetchone()['count']
                output = f"‏📜 API ها ({rowcount})\n\n"
                for row in result:
                    output += f"‏🔴️ Api ID: ‏<code>{row['api_id']}</code>\n"
                    output += f"‏🔴️ Api Hash: ‏<code>{row['api_hash']}</code>\n"
                    output += f"❌ حذف: /DeleteApi_{row['id']}\n\n"
                ob = utl.Pagination(update, "apis", output, utl.step_page, rowcount)
                return ob.process()
        if ex_data[0] == "d":
            cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={int(ex_data[1])}")
            row_user_select = cs.fetchone()
            if row_user_select is None:
                query.answer(text="❌ کاربر یافت نشد", show_alert=True)
                return message.delete()
            
            if ex_data[2] == "1" or ((ex_data[2] == "0" or ex_data[2] == "2") and row_user_select['status'] == 1):
                if from_id in utl.admins:
                    cs.execute(f"UPDATE {utl.users} SET status='{ex_data[2]}' WHERE user_id={row_user_select['user_id']}")
                else:
                    return query.answer(text="⛔️ این عملیات مخصوص ادمین اصلی است", show_alert=True)
            elif ex_data[2] == "2" or ex_data[2] == "0":
                cs.execute(f"UPDATE {utl.users} SET status='{ex_data[2]}' WHERE user_id={row_user_select['user_id']}")
            elif ex_data[2] == "sendmsg":
                cs.execute(f"UPDATE {utl.users} SET step='sendmsg;{row_user_select['user_id']}' WHERE user_id={from_id}")
                return message.reply_html(
                    text="پیام را ارسال کنید:",
                    reply_to_message_id=message_id,
                    reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                )
            else:
                return
            
            cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={row_user_select['user_id']}")
            row_user_select = cs.fetchone()
            admin_status = 0 if row_user_select['status'] == 1 else 1
            return message.edit_text(
                text=f"کاربر <a href='tg://user?id={row_user_select['user_id']}'>{row_user_select['user_id']}</a>",
                parse_mode='HTML',
                reply_markup={'inline_keyboard': [
                    [{'text': "ارسال پیام",'callback_data': f"d;{row_user_select['user_id']};sendmsg"}],
                    [{'text': ('ادمین ✅' if row_user_select['status'] == 1 else 'ادمین ❌'), 'callback_data': f"d;{row_user_select['user_id']};{admin_status}"}]
                ]}
            )
        if ex_data[0] == 'settings':
            if ex_data[1] == 'account_password':
                cs.execute(f"UPDATE {utl.users} SET step='{ex_data[0]};{ex_data[1]}' WHERE user_id={from_id}")
                return message.reply_html(
                    text="📌 پسورد جدید را وارد کنید:\n\n"
                        "⚠️ حداکثر 15 رقم می تواند باشد",
                    reply_to_message_id=message_id,
                    reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
                )
            if ex_data[1] == 'api_per_number':
                cs.execute(f"UPDATE {utl.users} SET step='{ex_data[0]};{ex_data[1]}' WHERE user_id={from_id}")
                return message.reply_html(
                    text="📌 در هر API چند اکانت ثبت شود؟\n\n"
                        "- هر چقدر تعداد کمتر باشد دیلیتی کمتر خواهد بود (کمترین مقدار: 1)\n\n"
                        "- میتونید از API های اکانت های دیگر هم استفاده کنید (لازم نیست حتما API که وارد می کنید مال اکانتی باشه که در ربات لاگین می کنید)\n\n"
                        "توصیه ما: 5 ارسال\n\n"
                        "‏- API را باید از سایت تلگرام تهیه کنید:\n"
                        "https://my.telegram.org/auth\n\n"
                        "آموزش دریافت api از تلگرام:\n"
                        "https://www.youtube.com/watch?v=po3VVpwJHXY",
                    reply_to_message_id=message_id,
                    disable_web_page_preview=True,
                    reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
                )
            if ex_data[1] == 'send_per_h':
                cs.execute(f"UPDATE {utl.users} SET step='{ex_data[0]};{ex_data[1]}' WHERE user_id={from_id}")
                return message.reply_html(
                    text="📌 هنگام ایجاد سفارش، هر اکانت چند ارسال انجام دهد؟\n\n"
                        "- تعداد 12 تا 18 خوب و حداکثر 28\n"
                        "- توصیه ما: 16 ارسال",
                    reply_to_message_id=message_id,
                    reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
                )
            if ex_data[1] == 'limit_per_h':
                cs.execute(f"UPDATE {utl.users} SET step='{ex_data[0]};{ex_data[1]}' WHERE user_id={from_id}")
                return message.reply_html(
                    text="📌 وقتی اکانت یک سفارش را انجام داد، چه مدت استراحت کند؟\n\n"
                        "- اگر غیرفعال کنید احتمال اسپم شدن و دیلتی زیاد خواهد بود\n"
                        "- توصیه ما: 24 ساعت\n\n"
                        "❕ مقدار با برحسب ساعت و برای غیرفعال کردن 0 را ارسال کنید",
                    reply_to_message_id=message_id,
                    reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
                )
            if ex_data[1] == 'change_pass' or ex_data[1] == 'exit_session' or ex_data[1] == 'is_change_profile' or ex_data[1] == 'is_set_username':
                row_admin[ex_data[1]] = 1 - row_admin[ex_data[1]]
                cs.execute(f"UPDATE {utl.admin} SET {ex_data[1]}={row_admin[ex_data[1]]}")
            return message.edit_reply_markup(
                reply_markup={'inline_keyboard': [
                    [{'text': f"📝 در هر API چند اکانت ثبت شود: {row_admin['api_per_number']} اکانت",'callback_data': "settings;api_per_number"}],
                    [{'text': f"📝 ارسال هر اکانت در هر استفاده: {row_admin['send_per_h']} ارسال",'callback_data': "settings;send_per_h"}],
                    [{'text': (f"📝 استفاده اکانت هر چند ساعت: " + (f"{int(row_admin['limit_per_h'] / 3600)} ساعت" if row_admin['limit_per_h'] > 0 else "غیرفعال ❌")),'callback_data': "settings;limit_per_h"}],
                    [{'text': f"🔐 رمز دو مرحله ای: " + (row_admin['account_password'] if row_admin['account_password'] is not None else "ثبت نشده") + "",'callback_data': "settings;account_password"}],
                    [{'text': ("تنظیم / تغییر رمز دو مرحله ای: " + ("فعال ✅" if row_admin['change_pass'] > 0 else "غیرفعال ❌")),'callback_data': "settings;change_pass"}],
                    [{'text': ("خروج از بقیه سشن ها: " + ("فعال ✅" if row_admin['exit_session'] > 0 else "غیرفعال ❌")),'callback_data': "settings;exit_session"}],
                    [{'text': ("تنظیم نام، بیو و پروفایل: " + ("فعال ✅" if row_admin['is_change_profile'] > 0 else "غیرفعال ❌")),'callback_data': "settings;is_change_profile"}],
                    [{'text': ("تنظیم یوزرنیم: " + ("فعال ✅" if row_admin['is_set_username'] > 0 else "غیرفعال ❌")),'callback_data': "settings;is_set_username"}],
                ]}
            )
        if ex_data[0] == 'change_status':
            cs.execute(f"SELECT * FROM {utl.orders} WHERE id={int(ex_data[1])}")
            row_orders = cs.fetchone()
            if row_orders is None:
                query.answer(text="❌ سفارش یافت نشد", show_alert=True)
                return message.delete()
            if ex_data[2] == '2':
                if row_orders['status'] == 1:
                    if len(ex_data) == 3:
                        return message.edit_reply_markup(
                            reply_markup={'inline_keyboard': [
                                [{'text': 'آیا سفارش پایان یابد؟', 'callback_data': "nazan"}],
                                [{'text': '❌ لغو ❌', 'callback_data': f"update;{row_orders['id']}"},{'text': '✅ بله ✅', 'callback_data': f"{ex_data[0]};{ex_data[1]};2;1"}]
                            ]}
                        )
                    if ex_data[3] == '1':
                        row_orders['status'] = 2
                        utl.end_order(cs, f"{directory}/files/exo_{row_orders['id']}_r.txt", row_orders)
            return message.edit_reply_markup(
                reply_markup={'inline_keyboard': [
                    [{'text': utl.status_orders[row_orders['status']], 'callback_data': "nazan"}],
                    [{'text': '🔄 بروزرسانی 🔄', 'callback_data': f"update;{row_orders['id']}"}]
                ]}
            )    
        if ex_data[0] == "analyze":
            cs.execute(f"SELECT * FROM {utl.egroup} WHERE id={int(ex_data[1])}")
            row_egroup = cs.fetchone()
            if row_egroup is None:
                return query.answer(text="❌ آنالیز یافت نشد", show_alert=True)
            
            cs.execute(f"UPDATE {utl.egroup} SET status=2 WHERE id={row_egroup['id']}")
            return message.edit_reply_markup(
                reply_markup={'inline_keyboard': [[{'text': "در حال اتمام ...",'callback_data': "nazan"}]]}
            )
        if ex_data[0] == "status_analyze":
            cs.execute(f"SELECT * FROM {utl.orders} WHERE WHERE id={int(ex_data[1])}")
            row_orders = cs.fetchone()
            if row_orders is None:
                return query.answer(text="❌ سفارش یافت نشد", show_alert=True)
            
            cs.execute(f"UPDATE {utl.orders} SET status_analyze=2 WHERE id={row_orders['id']}")
            return message.edit_reply_markup(
                reply_markup={'inline_keyboard': [[{'text': "در حال اتمام ...",'callback_data': "nazan"}]]}
            )
        if ex_data[0] == 'update':
            cs.execute(f"SELECT * FROM {utl.orders} WHERE id={int(ex_data[1])}")
            row_orders = cs.fetchone()
            if row_orders is None:
                return query.answer(text="❌ سفارش یافت نشد", show_alert=True)
            
            if row_orders['group_link'] is not None:
                output = f"\n🆔 <code>{row_orders['group_id']}</code>\n"
                output += f"🔗 {row_orders['group_link']}\n\n"
            else:
                output = "از طریق لیست انجام شده\n\n"
            if row_orders['cats'] is None:
                cats = "پشتیبانی نمی شود"
            else:
                where = ""
                cats = row_orders['cats'].split(",")
                for category in cats:
                    where += f"id={int(category)} OR "
                where = where[0:-4]
                cats = ""
                cs.execute(f"SELECT * FROM {utl.cats} WHERE {where}")
                result = cs.fetchall()
                for row in result:
                    cats += f"{row['name']},"
                cats = cats[0:-1]
            return message.edit_text(
                text=f"اطلاعات گروه: {output}"
                    f"👤 ارسال شده / درخواستی: [{row_orders['count_done']:,} / {row_orders['count']:,}]\n"
                    f"👤 در حال بررسی / همه: [{row_orders['count_request']:,} / {row_orders['max_users']:,}]\n\n"
                    f"🔵 گزارش اکانت ها\n"
                    f"      استفاده شده: {row_orders['count_acc']:,}\n"
                    f"      محدود شده: {row_orders['count_restrict']:,}\n"
                    f"      ریپورت شده: {row_orders['count_report']:,}\n"
                    f"      از دست رفته: {row_orders['count_accout']:,}\n\n"
                    f"🔴 گزارش درخواست های ارسال\n"
                    f"      خطا های اسپم: {row_orders['count_usrspam']:,}\n"
                    f"      یوزرنیم اشتباه: {row_orders['count_userincorrect']:,}\n"
                    f"      اکانت های محدود: {row_orders['count_restrict_error']:,}\n"
                    f"      خطا های دیگر: {row_orders['count_other_errors']:,}\n\n"
                    f"🟣 دسته بندی ها: {cats}\n"
                    f"🟣 تعداد ارسال هر اکانت: {row_orders['send_per_h']:,}\n\n"
                    f"📥 خروجی کاربران باقی مانده: /exo_{row_orders['id']}_r\n"
                    f"📥 خروجی کاربران منتقل شده: /exo_{row_orders['id']}_m\n"
                    "➖➖➖➖➖➖\n"
                    f"📅️ ایجاد: {jdatetime.datetime.fromtimestamp(row_orders['created_at']).astimezone(datetime.timezone(datetime.timedelta(hours=3, minutes=30))).strftime('%Y/%m/%d %H:%M:%S')}\n"
                    f"📅️ بروزرسانی: {jdatetime.datetime.fromtimestamp(row_orders['updated_at']).astimezone(datetime.timezone(datetime.timedelta(hours=3, minutes=30))).strftime('%Y/%m/%d %H:%M:%S')}\n"
                    f"📅 الان: {jdatetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=3, minutes=30))).strftime('%Y/%m/%d %H:%M:%S')}",
                parse_mode='HTML',
                disable_web_page_preview=True,
                reply_markup={'inline_keyboard': [
                    [{'text': utl.status_orders[row_orders['status']], 'callback_data': (f"change_status;{row_orders['id']};2" if row_orders['status'] == 1 else "nazan")}],
                    [{'text': '🔄 بروزرسانی 🔄', 'callback_data': f"update;{row_orders['id']}"}]
                ]}
            )
        if ex_data[0] == 'gc':
            if ex_data[1] == '1':
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE status=0")
                result = cs.fetchall()
                if not result:
                    return query.answer(text="❌ هیچ اکانتی یافت نشد", show_alert=True)
                
                for row_mbots in result:
                    try:
                        cs.execute(f"DELETE FROM {utl.mbots} WHERE id={row_mbots['id']}")
                        os.remove(f"{directory}/sessions/{row_mbots['uniq_id']}.session")
                    except:
                        pass
                return message.reply_html(text=f"✅ {len(result)} اکانت لاگ اوت شده حذف شدند")


def private_process(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    bot = context.bot
    message = update.message
    from_id = message.from_user.id
    chat_id = message.chat.id
    message_id = message.message_id
    text = message.text if message.text else ""
    if message.text:
        txtcap = message.text
    elif message.caption:
        txtcap = message.caption
    else:
        txtcap = ""
    ex_text = text.split('_')
    timestamp = int(time.time())

    cs = utl.Database()
    cs = cs.data()

    cs.execute(f"SELECT * FROM {utl.admin}")
    row_admin = cs.fetchone()
    cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={from_id}")
    row_user = cs.fetchone()
    if row_user is None:
        uniq_id = utl.unique_id()
        cs.execute(f"INSERT INTO {utl.users} (user_id,status,step,created_at,uniq_id) VALUES ({from_id},0,'start',{timestamp},'{uniq_id}')")
        cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={from_id}")
        row_user = cs.fetchone()
    ex_step = row_user['step'].split(';')
    
    if from_id in utl.admins or row_user['status'] == 1:
        if text == '/start' or text == '/panel' or text == utl.menu_var:
            user_panel(message=message)
            cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
            return cs.execute(f"DELETE FROM {utl.orders} WHERE user_id={from_id} AND status=0")
        if text == '/restart':
            info_msg = message.reply_html(text="در حال بررسی ...")
            os.system(f"{utl.python_version} \"{directory}/run.py\"")
            return info_msg.edit_text(text="✅ انجام شد")
        if ex_step[0] == 'set_cache':
            if not message.forward_from_chat:
                return message.reply_html(text="❌ یک پست از کانال فوروارد کنید", reply_to_message_id=message_id)
            if not message.forward_from_chat.username:
                return message.reply_html(text="❌ کانال باید عمومی باشد", reply_to_message_id=message_id)
            if bot.get_chat_member(chat_id=message.forward_from_chat.id, user_id=utl.bot_id).status == "left":
                return message.reply_html(text="❌ ربات باید در کانال ادمین باشد", reply_to_message_id=message_id)
            
            cs.execute(f"UPDATE {utl.admin} SET cache='{message.forward_from_chat.username}'")
            cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id={from_id}")
            return user_panel(message=message, text="✅ کانال کش با موفقیت ثبت شد", reply_to_message_id=message_id)
        if row_admin['cache'] is None or text == "📣 کانال کش":
            cs.execute(f"UPDATE {utl.users} SET step='set_cache;none' WHERE user_id={from_id}")
            return message.reply_html(
                text="برای ثبت کانال کش یک پست از کانال به اینجا فوروارد کنید:\n\n"
                    "❕ پیام هایی که قرار است به کاربران ارسال شود ابتدا در این کانال ذخیره می شوند، تا ربات موقع ارسال به آن ها دسترسی داشته باشد",
                reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
            )
        if ex_step[0] == 'info_user':
            try:
                user_id = int(text)
            except:
                return message.reply_html(text="❌ ورودی نامعتبر", reply_to_message_id=message_id)
            cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={user_id}")
            row_user_select = cs.fetchone()
            if row_user_select is None:
                return message.reply_html(
                    text="❌ آیدی عددی اشتباه است\n\n"
                        "❕ دقت کنید که کاربر قبلا باید ربات را استارت کرده باشد",
                    reply_to_message_id=message_id
                )
            admin_status = 0 if row_user_select['status'] == 1 else 1
            message.reply_html(
                text=f"کاربر <a href='tg://user?id={row_user_select['user_id']}'>{row_user_select['user_id']}</a>",
                reply_markup={'inline_keyboard': [
                    [{'text': "ارسال پیام",'callback_data': f"d;{row_user_select['user_id']};sendmsg"}],
                    [{'text': ('ادمین ✅' if row_user_select['status'] == 1 else 'ادمین ❌'), 'callback_data': f"d;{row_user_select['user_id']};{admin_status}"}]
                ]}
            )
            cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
            return user_panel(message=message)
        if ex_step[0] == 'sendmsg':
            cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={int(ex_step[1])}")
            row_user_select = cs.fetchone()
            if row_user_select is None:
                return message.reply_html(text="❌ کاربر یافت نشد", reply_to_message_id=message_id)
            if not message.text and not message.photo and message.video and message.audio and message.voice and message.document:
                return message.reply_html(text="⛔️ پیام پشتیبانی نمی شود", reply_to_message_id=message_id)
            try:
                content = f"📧️ پیام از طرف پشتیبانی\n——————————————————\n{txtcap}"
                if message.text:
                    bot.send_message(chat_id=row_user_select['user_id'], text=content, parse_mode='HTML', disable_web_page_preview=True)
                elif message.photo:
                    bot.send_photo(chat_id=row_user_select['user_id'], caption=content, photo=message.photo[len(message.photo) - 1].file_id, parse_mode='HTML')
                elif message.video:
                    bot.send_video(chat_id=row_user_select['user_id'], video=message.video.file_id, caption=content, parse_mode='HTML')
                elif message.audio:
                    bot.send_audio(chat_id=row_user_select['user_id'], audio=message.audio.file_id, caption=content, parse_mode='HTML')
                elif message.voice:
                    bot.send_voice(chat_id=row_user_select['user_id'], voice=message.voice.file_id, caption=content, parse_mode='HTML')
                elif message.document:
                    bot.send_document(chat_id=row_user_select['user_id'], document=message.document.file_id, caption=content, parse_mode='HTML')
                cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id={from_id}")
                return user_panel(message=message, text="✅ پیام با موفقیت ارسال شد", reply_to_message_id=message_id)
            except:
                return message.reply_html(text="❌ خطای ناشناخته، مجدد تلاش کنید", reply_to_message_id=message_id)
        if ex_step[0] == 'add_api':
            try:
                ex_nl_text = text.split("\n")
                if len(ex_nl_text) != 2 or len(ex_nl_text[0]) > 50 or len(ex_nl_text[1]) > 200:
                    return message.reply_html(text="❌ ورودی اشتباه است", reply_to_message_id=message_id)
                if not re.findall('^[0-9]*$', ex_nl_text[0]):
                    return message.reply_html(text="‏❌ api id اشتیاه است", reply_to_message_id=message_id)
                if not re.findall('^[0-9-a-z-A-Z]*$', ex_nl_text[1]):
                    return message.reply_html(text="‏❌ api hash اشتیاه است", reply_to_message_id=message_id)
                
                api_id = ex_nl_text[0]
                api_hash = ex_nl_text[1]
                cs.execute(f"SELECT * FROM {utl.apis} WHERE api_id='{api_id}' OR api_hash='{api_hash}'")
                if cs.fetchone() is not None:
                    return message.reply_html(text="❌ این API قبل افزوده شده است", reply_to_message_id=message_id)
                
                cs.execute(f"INSERT INTO {utl.apis} (api_id,api_hash) VALUES ('{api_id}','{api_hash}')")
                return message.reply_html(
                    text="✅ با موفقیت اضافه شده\n\n"
                        "مورد دیگری اضافه کنید:",
                    reply_to_message_id=message_id,
                    reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
                )
            except:
                return message.reply_html(text="❌ ورودی اشتباه", reply_to_message_id=message_id)
        if ex_step[0] == 'create_cat':
            cs.execute(f"SELECT * FROM {utl.cats} WHERE name='{text}'")
            row_cats = cs.fetchone()
            if row_cats is not None:
                return message.reply_html(text="❌ دسته بندی قبلا ایجاد شده است", reply_to_message_id=message_id)
            else:
                cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
                cs.execute(f"INSERT INTO {utl.cats} (name) VALUES ('{text}')")
                return user_panel(message=message, text="✅ با موفقیت ایجاد شد", reply_to_message_id=message_id)
        if ex_step[0] == 'set_cat':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_step[1])}")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                return message.reply_html(text="❌ اکانت یافت نشد", reply_to_message_id=message_id)
            cs.execute(f"SELECT * FROM {utl.cats} WHERE name='{text}'")
            row_cats = cs.fetchone()
            if row_cats is None:
                return message.reply_html(text="❌ دسته بندی یافت نشد", reply_to_message_id=message_id)
            
            cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
            cs.execute(f"UPDATE {utl.mbots} SET cat_id={row_cats['id']} WHERE id={row_mbots['id']}")
            return message.reply_html(
                text="✅ با موفقیت بروزرسانی شد",
                reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
            )
        if ex_step[0] == 'analyze':
            if ex_step[1] == 'type':
                if text == 'کاربران':
                    cs.execute(f"UPDATE {utl.users} SET step='analyze;users;link' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="لینک گروه را ارسال کنید:",
                        reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
                    )
                if text == 'پیام ها':
                    cs.execute(f"UPDATE {utl.users} SET step='analyze;messages;link' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="لینک گروه را ارسال کنید:",
                        reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
                    )
                return message.reply_html(text="⛔️ از منو انتخاب کنید", reply_to_message_id=message_id)
            if ex_step[1] == 'users':
                if ex_step[2] == 'link':
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 ORDER BY RAND()")
                    row_mbots = cs.fetchone()
                    if row_mbots is None:
                        return message.reply_html(text="❌ هیچ اکانتی یافت نشد", reply_to_message_id=message_id)
                    uniq_id = utl.unique_id()
                    try:
                        int(text)
                        cs.execute(f"INSERT INTO {utl.egroup} (type,user_id,chat_id,status,created_at,updated_at,uniq_id) VALUES (0,{from_id},'{text}',0,{timestamp},{timestamp},'{uniq_id}')")
                    except:
                        text = text.replace("/+", "/joinchat/")
                        cs.execute(f"INSERT INTO {utl.egroup} (type,user_id,link,status,created_at,updated_at,uniq_id) VALUES (0,{from_id},'{text}',0,{timestamp},{timestamp},'{uniq_id}')")
                    cs.execute(f"SELECT * FROM {utl.egroup} WHERE uniq_id='{uniq_id}'")
                    row_egroup = cs.fetchone()
                    if row_egroup is None:
                        return message.reply_html(text="❌ خطای ناشناخته، مجدد تلاش کنید", reply_to_message_id=message_id)
                    cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{ex_step[1]};account;{row_egroup['id']}' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="آیدی عددی اکانت رو ارسال کنید:",
                        reply_markup={'resize_keyboard': True, 'keyboard': [
                            [{'text': "اکانت رندوم"}],
                            [{'text': utl.menu_var}]
                        ]}
                    )
                elif ex_step[2] == 'account':
                    cs.execute(f"SELECT * FROM {utl.egroup} WHERE id={int(ex_step[3])}")
                    row_egroup = cs.fetchone()
                    if row_egroup is None:
                        return message.reply_html(text="❌ خطای ناشناخته، مجدد تلاش کنید", reply_to_message_id=message_id)
                    if text == "اکانت رندوم":
                        cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 ORDER BY RAND()")
                    else:
                        cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 AND user_id={int(text)}")
                    row_mbots = cs.fetchone()
                    if row_mbots is None:
                        return message.reply_html(text="❌ هیچ اکانتی یافت نشد", reply_to_message_id=message_id)
                    
                    cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
                    info_msg = message.reply_html(text="در حال اتصال ...", reply_to_message_id=message_id)
                    os.system(f"{utl.python_version} \"{directory}/tl_analyze.py\" {row_mbots['uniq_id']} {from_id} {row_egroup['id']} users {info_msg.message_id}")
                    user_panel(message=message)
                    return info_msg.delete()
            if ex_step[1] == 'messages':
                if ex_step[2] == 'link':
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 ORDER BY RAND()")
                    row_mbots = cs.fetchone()
                    if row_mbots is None:
                        return message.reply_html(text="❌ هیچ اکانتی یافت نشد", reply_to_message_id=message_id)
                    uniq_id = utl.unique_id()
                    try:
                        int(text)
                        cs.execute(f"INSERT INTO {utl.egroup} (type,user_id,chat_id,status,created_at,updated_at,uniq_id) VALUES (1,{from_id},'{text}',0,'{timestamp}','{timestamp}','{uniq_id}')")
                    except:
                        text = text.replace("/+", "/joinchat/")
                        cs.execute(f"INSERT INTO {utl.egroup} (type,user_id,link,status,created_at,updated_at,uniq_id) VALUES (1,{from_id},'{text}',0,'{timestamp}','{timestamp}','{uniq_id}')")
                    cs.execute(f"SELECT * FROM {utl.egroup} WHERE uniq_id='{uniq_id}'")
                    row_egroup = cs.fetchone()
                    if row_egroup is None:
                        return message.reply_html(text="❌ خطای ناشناخته، مجدد تلاش کنید", reply_to_message_id=message_id)
                    
                    cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{ex_step[1]};account;{row_egroup['id']}' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="آیدی عددی اکانت رو ارسال کنید:",
                        reply_markup={'resize_keyboard': True, 'keyboard': [
                            [{'text': "اکانت رندوم"}],
                            [{'text': utl.menu_var}]
                        ]}
                    )
                elif ex_step[2] == 'account':
                    cs.execute(f"SELECT * FROM {utl.egroup} WHERE id={int(ex_step[3])}")
                    row_egroup = cs.fetchone()
                    if row_egroup is None:
                        return message.reply_html(text="❌ خطای ناشناخته، مجدد تلاش کنید", reply_to_message_id=message_id)
                    if text == "اکانت رندوم":
                        cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 ORDER BY RAND()")
                    else:
                        cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 AND user_id={int(text)}")
                    row_mbots = cs.fetchone()
                    if row_mbots is None:
                        return message.reply_html(text="❌ هیچ اکانتی یافت نشد", reply_to_message_id=message_id)
                    
                    cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
                    info_msg = message.reply_html(text="در حال اتصال ...", reply_to_message_id=message_id)
                    os.system(f"{utl.python_version} \"{directory}/tl_analyze.py\" {row_mbots['uniq_id']} {from_id} {row_egroup['id']} messages {info_msg.message_id}")
                    user_panel(message=message)
                    return info_msg.delete()
        if ex_step[0] == 'settings':
            if ex_step[1] == 'account_password':
                if len(text) > 15:
                    return message.reply_html(text="❌ ورودی نامعتبر", reply_to_message_id=message_id)
                cs.execute(f"UPDATE {utl.admin} SET {ex_step[1]}='{text}'")
                cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
                return user_panel(message=message, text="✅ با موفقیت بروزرسانی شد", reply_to_message_id=message_id)
            if ex_step[1] == 'api_per_number':
                try:
                    api_per_number = int(text)
                    if api_per_number < 1:
                        return message.reply_html(text="❌ ورودی نامعتبر", reply_to_message_id=message_id)
                except:
                    return message.reply_html(text="❌ ورودی نامعتبر", reply_to_message_id=message_id)
                cs.execute(f"UPDATE {utl.admin} SET {ex_step[1]}={api_per_number}")
                cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
                return user_panel(message=message, text="✅ با موفقیت بروزرسانی شد", reply_to_message_id=message_id)
            if ex_step[1] == 'send_per_h':
                try:
                    send_per_h = int(text)
                    if send_per_h < 1:
                        return message.reply_html(text="❌ ورودی نامعتبر", reply_to_message_id=message_id)
                except:
                    return message.reply_html(text="❌ ورودی نامعتبر", reply_to_message_id=message_id)
                cs.execute(f"UPDATE {utl.admin} SET {ex_step[1]}={send_per_h}")
                cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
                return user_panel(message=message, text="✅ با موفقیت بروزرسانی شد", reply_to_message_id=message_id)
            if ex_step[1] == 'limit_per_h':
                try:
                    limit_per_h = int(text) * 3600
                    if limit_per_h < 0:
                        return message.reply_html(text="❌ ورودی نامعتبر", reply_to_message_id=message_id)
                except:
                    return message.reply_html(text="❌ ورودی نامعتبر", reply_to_message_id=message_id)
                cs.execute(f"UPDATE {utl.admin} SET {ex_step[1]}={limit_per_h}")
                cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
                return user_panel(message=message, text="✅ با موفقیت بروزرسانی شد", reply_to_message_id=message_id)
        if ex_step[0] == 'add_acc':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_step[1])}")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                return message.reply_html(text="❌ خطای ناشناخته، مجدد تلاش کنید", reply_to_message_id=message_id)
            if ex_step[2] == 'type':
                if text == 'شماره':
                    cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{row_mbots['id']};number;phone' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="شماره را به هماره کد کشور وارد کنید:",
                        reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                    )
                if text == 'سشن':
                    cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{row_mbots['id']};session' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="فایل سشن تلتون را ارسال کنید:",
                        reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                    )
                if text == 'زیپ':
                    cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{row_mbots['id']};zip' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="فایل های سشن تلتون را داخل یک فایل زیپ ارسال کنید:",
                        reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                    )
                return message.reply_html(text="⛔️ از منو انتخاب کنید", reply_to_message_id=message_id)
            if ex_step[2] == 'session':
                if not message.document or message.document.file_name[-8:] != ".session":
                    return message.reply_html(text="❌ فایل باید از نوع سشن تلتون باشد", reply_to_message_id=message_id)
                row_apis = utl.select_api(cs, row_admin['api_per_number'])
                if row_apis is None:
                    return message.reply_html(text="❌ ابتدا یک API اضافه کنید یا از تنظیمات گزینه اول را افزایش دهید", reply_to_message_id=message_id)
                try:
                    unique_id = utl.unique_id()
                    cs.execute(f"INSERT INTO {utl.mbots} (cat_id,creator_user_id,api_id,api_hash,status,created_at,uniq_id) VALUES (1,{from_id},'{row_apis['api_id']}','{row_apis['api_hash']}',0,{int(time.time())},'{unique_id}')")
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE uniq_id='{unique_id}'")
                    row_mbots_select = cs.fetchone()
                    if row_mbots_select is None:
                        return message.reply_html(text="❌ خطای ناشناخته، مجدد تلاش کنید", reply_to_message_id=message_id)
                    info_action = bot.get_file(message.document.file_id)
                    with open(f"{directory}/sessions/{row_mbots_select['uniq_id']}.session", "wb") as file:
                        file.write(requests.get(info_action.file_path).content)
                    info_msg = message.reply_html(text="در حال بررسی ...")
                    os.system(f"{utl.python_version} \"{directory}/tl_import.py\" {row_mbots_select['uniq_id']}")
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={row_mbots_select['id']}")
                    row_mbots_select = cs.fetchone()
                    if row_mbots_select is not None:
                        if row_mbots_select['status'] == 1:
                            return info_msg.edit_text(text=f"✅ ذخیره شد: <code>{row_mbots_select['phone']}</code>", parse_mode="html")
                        else:
                            cs.execute(f"DELETE FROM {utl.mbots} WHERE id={row_mbots_select['id']}")
                            return info_msg.edit_text(text=f"❕ قبلا اضافه شده: <code>{row_mbots_select['phone']}</code>", parse_mode="html")
                    else:
                        return info_msg.edit_text(text="❌ سشن معتبر نیست")
                except:
                    return message.reply_html(text="❌ خطای ناشناخته، مجدد تلاش کنید", reply_to_message_id=message_id)
            if ex_step[2] == 'zip':
                cs.execute(f"DELETE FROM {utl.mbots} WHERE creator_user_id={from_id} AND status=0 AND user_id IS NULL")
                if not message.document or message.document.file_name[-4:] != ".zip":
                    return message.reply_html(text="❌ فایل باید از نوع زیپ فایل", reply_to_message_id=message_id)
                try:
                    try:
                        shutil.rmtree(f"{directory}/import")
                    except:
                        pass
                    if not os.path.exists(f"{directory}/import"):
                        os.mkdir(f"{directory}/import")
                    info_msg = message.reply_html(text="در حال دانلود ...", reply_to_message_id=message_id)
                    info_action = bot.get_file(message.document.file_id)
                    with open(f"{directory}/file.zip", "wb") as file:
                        file.write(requests.get(info_action.file_path).content)
                    
                    info_msg.edit_text(text="در حال آنالیز ...")
                    with zipfile.ZipFile(f"{directory}/file.zip", 'r') as zObject:
                        zObject.extractall(path=f"{directory}/import")
                    os.remove(f"{directory}/file.zip")
                    
                    info_msg.edit_text(text="در حال انجام عملیات ...")
                    list_files = os.listdir(f"{directory}/import")
                    count_all = len(list_files)
                    count_import_success = count_import_failed = count_import_existed = 0
                    for file in list_files:
                        row_apis = utl.select_api(cs, row_admin['api_per_number'])
                        if row_apis is None:
                            message.reply_html(text="❌ ابتدا یک API اضافه کنید یا از تنظیمات گزینه اول را افزایش دهید", reply_to_message_id=message_id)
                            break
                        if file[-8:] == ".session":
                            try:
                                unique_id = utl.unique_id()
                                cs.execute(f"INSERT INTO {utl.mbots} (cat_id,creator_user_id,api_id,api_hash,status,created_at,uniq_id) VALUES (1,{from_id},'{row_apis['api_id']}','{row_apis['api_hash']}',0,{int(time.time())},'{unique_id}')")
                                cs.execute(f"SELECT * FROM {utl.mbots} WHERE uniq_id='{unique_id}'")
                                row_mbots = cs.fetchone()
                                with open(f"{directory}/import/{file}", "rb") as file:
                                    content = file.read()
                                with open(f"{directory}/sessions/{row_mbots['uniq_id']}.session", "wb") as file:
                                    file.write(content)
                                os.system(f"{utl.python_version} \"{directory}/tl_import.py\" {row_mbots['uniq_id']}")
                                cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={row_mbots['id']}")
                                row_mbots = cs.fetchone()
                                if row_mbots is not None:
                                    if row_mbots['status'] == 1:
                                        count_import_success += 1
                                    else:
                                        count_import_existed += 1
                                        cs.execute(f"DELETE FROM {utl.mbots} WHERE id={row_mbots['id']}")
                                else:
                                    count_import_failed += 1
                            except:
                                pass
                            try:
                                info_msg.edit_text(
                                    text="در حال انجام عملیات ...\n"
                                        f"⏳ در حال بررسی: [{(count_import_success + count_import_failed + count_import_existed):,} / {count_all:,}]\n\n"
                                        f"✅ موفق: {count_import_success:,}\n"
                                        f"❌ ناموفق: {count_import_failed:,}\n"
                                        f"❕ قبلا اضافه شده: {count_import_existed:,}\n"
                                )
                            except:
                                pass
                    info_msg.reply_html(
                        text=f"عملیات پایان یافت: [{(count_import_success + count_import_failed + count_import_existed):,} / {count_all:,}]\n\n"
                            f"✅ موفق: {count_import_success:,}\n"
                            f"❌ ناموفق: {count_import_failed:,}\n"
                            f"❕ قبلا اضافه شده: {count_import_existed:,}\n"
                    )
                    try:
                        shutil.rmtree(f"{directory}/import")
                    except:
                        pass
                    return
                except Exception as e:
                    print(e)
                    return message.reply_html(text="❌ خطای ناشناخته، مجدد تلاش کنید", reply_to_message_id=message_id)
            if ex_step[2] == 'number':
                if ex_step[3] == 'phone':
                    phone = text.replace("+","").replace(" ","")
                    if not re.findall('^[0-9]*$', phone):
                        return message.reply_html(text="❌ شماره اشتباه است", reply_to_message_id=message_id)
                    
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE phone='{phone}' AND status>0")
                    row_mbots_select = cs.fetchone()
                    if row_mbots_select is not None:
                        return message.reply_html(text="❌ شماره قبلا اضافه شده است", reply_to_message_id=message_id)
                    cs.execute(f"UPDATE {utl.mbots} SET phone='{phone}' WHERE id={row_mbots['id']}")
                    info_msg = message.reply_html(text="در حال اتصال ...", reply_to_message_id=message_id)
                    os.system(f"{utl.python_version} \"{directory}/tl_account.py\" {row_mbots['uniq_id']} {from_id} {info_msg.message_id}")
                    return info_msg.delete()
                if ex_step[3] == 'code':
                    try:
                        code = int(text)
                    except:
                        pass
                    return cs.execute(f"UPDATE {utl.mbots} SET code={code} WHERE id={row_mbots['id']}")
                if ex_step[3] == 'password':
                    return cs.execute(f"UPDATE {utl.mbots} SET password='{text}' WHERE id={row_mbots['id']}")
        if ex_step[0] == 'create_order':
            cs.execute(f"SELECT * FROM {utl.orders} WHERE id={int(ex_step[1])}")
            row_orders = cs.fetchone()
            if row_orders is None:
                return message.reply_html(text="❌ سفارش یافت نشد، مجدد تلاش کنید", reply_to_message_id=message_id)
            if ex_step[2] == 'category':
                if text == "⏩ بعدی":
                    if row_orders['cats'] is None:
                        return message.reply_html(text="❌ حداقل باید یک دسته بندی را انتخاب کنید", reply_to_message_id=message_id)
                    cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{ex_step[1]};type_send' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="آیا می خواهید کاربران تکراری حدف شوند؟",
                        reply_markup={'resize_keyboard': True,'keyboard': [
                            [{'text': 'خیر'}, {'text': 'بله'}],
                            [{'text': utl.menu_var}]
                        ]}
                    )
                else:
                    cs.execute(f"SELECT * FROM {utl.cats} WHERE name='{text}'")
                    row_cats = cs.fetchone()
                    if row_cats is None:
                        return message.reply_html(text="❌ دسته بندی یافت نشد", reply_to_message_id=message_id)
                    cats = ""
                    if row_orders['cats'] is not None:
                        cats = row_orders['cats'].split(",")
                        for category in cats:
                            try:
                                if int(category) == row_cats['id']:
                                    return message.reply_html(text=f"❌ دسته بندی <b>{row_cats['name']}</b> قبلا انتخاب شده است", reply_to_message_id=message_id)
                            except:
                                pass
                        cats = f"{row_orders['cats']},{row_cats['id']}"
                    else:
                        cats = row_cats['id']
                    row_orders['cats'] = str(cats)
                    
                    where = ""
                    cats = row_orders['cats'].split(",")
                    for category in cats:
                        where += f"cat_id={int(category)} OR "
                    where = where[0:-4]
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status=1 AND ({where}) LIMIT 1")
                    if cs.fetchone() is None:
                        return message.reply_html(text="❌ هیچ اکانت فعالی در این دسته بندی وجود ندارد", reply_to_message_id=message_id)
                    
                    cs.execute(f"UPDATE {utl.orders} SET cats='{row_orders['cats']}' WHERE id={row_orders['id']}")
                    keyboard = [[{'text': utl.menu_var}, {'text': "⏩ بعدی"}]]
                    cs.execute(f"SELECT * FROM {utl.cats}")
                    result = cs.fetchall()
                    for row in result:
                        keyboard.append([{'text': row['name']}])
                    return message.reply_html(
                        text=f"✅ دسته بندی <b>{row_cats['name']}</b> انتخاب شد\n\n"+
                            "روی گزینه <b>⏩ بعدی</b> بزنید یا یک دسته بندی دیگر انتخاب کنید:",
                        reply_markup={'resize_keyboard': True, 'keyboard': keyboard}
                    )
            if ex_step[2] == 'type_send':
                if text == 'خیر':
                    type_send = 0
                elif text == 'بله':
                    type_send = 1
                else:
                    return message.reply_html(text="⛔️ از منو انتخاب کنید", reply_to_message_id=message_id)
                cs.execute(f"UPDATE {utl.orders} SET type_send={type_send} WHERE id={row_orders['id']}")
                cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{ex_step[1]};type' WHERE user_id={from_id}")
                return message.reply_html(
                    text="نوع سفارش را انتخاب کنید:",
                    reply_markup={'resize_keyboard': True,'keyboard': [
                        [{'text': "🔴 لینک گروه 🔴"}],
                        [{'text': "🔵 لیست اعضا 🔵"}],
                        [{'text': utl.menu_var}]
                    ]}
                )
            if ex_step[2] == 'type':
                if text == "🔴 لینک گروه 🔴":
                    cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{ex_step[1]};link;info' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="مطابق نمونه ارسال کنید:\n\n"
                            "لینک گروه (خط اول)\n"
                            "تعداد ارسال (خط دوم)\n\n"
                            "مثال:\n"
                            "https://t.me/group\n"
                            "100",
                        disable_web_page_preview=True,
                        reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
                    )
                if text == "🔵 لیست اعضا 🔵":
                    cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{ex_step[1]};list;info' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="هر کدام از یوزرنیم ها را در یک خط داخل یک فایل txt وارد کنید و فایل را ارسال کنید:",
                        reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
                    )
                return message.reply_html(text="⛔️ از منو انتخاب کنید", reply_to_message_id=message_id)
            if ex_step[2] == 'link':
                if ex_step[3] == 'info':
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 ORDER BY RAND()")
                    row_mbots = cs.fetchone()
                    if row_mbots is None:
                        return message.reply_html(text="❌ هیچ اکانتی یافت نشد", reply_to_message_id=message_id)
                    try:
                        ex_nl_text = text.split("\n")
                        group_link = ex_nl_text[0].replace("/+","/joinchat/")
                        count = int(ex_nl_text[1])
                        ex_nl_text = text.split("\n")
                        if len(group_link) > 200 or len(ex_nl_text) != 2:
                            return message.reply_html(text="❌ ورودی نامعتبر", reply_to_message_id=message_id)
                        if group_link[0:13] != "https://t.me/":
                            return message.reply_html(text="❌ لینک گروه اشتباه است", reply_to_message_id=message_id)
                        
                        cs.execute(f"UPDATE {utl.orders} SET group_link='{group_link}',count={count} WHERE id={row_orders['id']}")
                        info_msg = message.reply_html(text="در حال اتصال ...", reply_to_message_id=message_id)
                        os.system(f"{utl.python_version} \"{directory}/tl_analyze.py\" {row_mbots['uniq_id']} {from_id} {row_orders['id']} analyze {info_msg.message_id}")
                        return info_msg.delete()
                    except:
                        return message.reply_html(text="❌ خطای ناشناخته، مجدد تلاش کنید", reply_to_message_id=message_id)
                if ex_step[3] == 'type_users':
                    if text == "همه کاربران":
                        type_users = 0
                    elif text == "کاربران واقعی":
                        type_users = 1
                        cs.execute(f"DELETE FROM {utl.analyze} WHERE order_id={row_orders['id']} AND is_real=0")
                    elif text == "کاربران فیک":
                        type_users = 2
                        cs.execute(f"DELETE FROM {utl.analyze} WHERE order_id={row_orders['id']} AND is_fake=0")
                    elif text == "کاربران آنلاین":
                        type_users = 3
                        cs.execute(f"DELETE FROM {utl.analyze} WHERE order_id={row_orders['id']} AND is_online=0")
                    elif text == "کاربران با شماره":
                        type_users = 4
                        cs.execute(f"DELETE FROM {utl.analyze} WHERE order_id={row_orders['id']} AND is_phone=0")
                    else:
                        return message.reply_html(text="⛔️ فقط از منو انتخاب کنید", reply_to_message_id=message_id)
                    
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.analyze}")
                    max_users = cs.fetchone()['count']
                    cs.execute(f"UPDATE {utl.orders} SET max_users={max_users},type_users={type_users},send_per_h={row_admin['send_per_h']},created_at={timestamp},updated_at={timestamp} WHERE id={row_orders['id']}")
                    cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{ex_step[1]};get_message' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="پیامی که میخواهید به کاربران بفرستید را ارسال کنید:",
                        reply_to_message_id=message_id,
                        reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                    )
            if ex_step[2] == 'list':
                if ex_step[3] == 'info':
                    if not message.document:
                        return message.reply_html(text="❌ فقط یک فایل txt ارسال کنید", reply_to_message_id=message_id)
                    
                    info_msg = message.reply_html(text="در حال بررسی ...", reply_to_message_id=message_id)
                    try:
                        list_members = []
                        info_action = bot.get_file(message.document.file_id)
                        with open(f"{directory}/files/id-{row_orders['id']}.txt", "wb") as file:
                            file.write(requests.get(info_action.file_path).content)
                        with open(f"{directory}/files/id-{row_orders['id']}.txt", "rb") as file:
                            result = file.read().splitlines()
                            for value in result:
                                value = value.decode('utf8')
                                if value == "" or len(value) < 5:
                                    continue
                                elif value[0:1] != "@":
                                    value = f"@{value}"
                                if not value in list_members:
                                    list_members.append(value)
                        cs.execute(f"DELETE FROM {utl.analyze}")
                        for i, value in enumerate(list_members):
                            batch = int((i // 3) + 1)
                            cs.execute(
                                f"INSERT INTO {utl.analyze} (order_id,user_id,username,is_real,created_at,batch) "
                                f"VALUES ({row_orders['id']},0,'{value}',1,{timestamp},{batch})"
                            )
                        if row_orders['type_send'] == 1:
                            i = 0
                            timestamp_start = timestamp = int(time.time())
                            cs.execute(f"SELECT {utl.analyze}.id as id,{utl.analyze}.username as username FROM {utl.analyze} INNER JOIN {utl.reports} ON {utl.analyze}.username={utl.reports}.username GROUP BY {utl.reports}.username")
                            count = cs.rowcount
                            result_detect_members = cs.fetchall()
                            for row in result_detect_members:
                                try:
                                    cs.execute(f"DELETE FROM {utl.analyze} WHERE username='{row['username']}'")
                                    if (int(time.time()) - timestamp_start) > 5:
                                        timestamp_start = int(time.time())
                                        info_msg.edit_text(
                                            text="⏳ در حال جدا سازی کاربران...\n\n"+
                                                f"🔗 لینک: {row_orders['group_link']}\n"+
                                                f"♻️ در حال پیشرفت: {(i / count * 100):.2f}%\n"+
                                                "➖➖➖➖➖➖\n"+
                                                f"📅 مدت زمان: {jdatetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=3, minutes=30))).strftime('%H:%M:%S')}\n"+
                                                f"📅 زمان حال: {utl.convert_time((timestamp_start - timestamp), 2)}",
                                            disable_web_page_preview=True,
                                        )
                                except:
                                    pass
                                i += 1

                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.analyze}")
                        max_users = cs.fetchone()['count']
                        cs.execute(f"UPDATE {utl.orders} SET max_users={max_users},count={max_users},type_users=0,send_per_h={row_admin['send_per_h']},created_at={timestamp},updated_at={timestamp} WHERE id={row_orders['id']}")
                        cs.execute(f"SELECT MAX(batch) as max_batch FROM {utl.analyze} WHERE order_id={row_orders['id']}")
                        max_batch = cs.fetchone()['max_batch']
                        max_batch = int(max_batch) if max_batch is not None else 1
                        cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{ex_step[1]};get_message;1;1' WHERE user_id={from_id}")
                        message.reply_html(
                            text=f"بتچ بندی انجام شد: {max_batch} بتچ (هر بتچ 3 نفر)\n\n"
                                "پیام شماره 1 برای بتچ 1 را ارسال کنید:",
                            reply_to_message_id=message_id,
                            reply_markup={'resize_keyboard': True,'keyboard': [
                                [{'text': "✅ پایان ✅"}],
                                [{'text': utl.menu_var}]
                            ]}
                        )
                    except:
                        message.reply_html(text="❌ هنگام آنالیز فایل خطایی رخ داد", reply_to_message_id=message_id)
                    return info_msg.delete()
            if ex_step[2] == "get_message":
                batch = 1
                msg_index = 1
                try:
                    if len(ex_step) >= 5:
                        batch = int(ex_step[3])
                        msg_index = int(ex_step[4])
                except:
                    batch = 1
                    msg_index = 1

                cs.execute(f"SELECT MAX(batch) as max_batch FROM {utl.analyze} WHERE order_id={row_orders['id']}")
                max_batch = cs.fetchone()['max_batch']
                max_batch = int(max_batch) if max_batch is not None else 1

                if text != "✅ پایان ✅":
                    if not message.text and not message.photo and message.video and message.audio and message.voice and message.document:
                        return message.reply_html(text="⛔️ پیام پشتیبانی نمی شود", reply_to_message_id=message_id)
                    try:
                        uniq_id = utl.unique_id()
                        if message.text:
                            info_msg = bot.send_message(chat_id=f"@{row_admin['cache']}", disable_web_page_preview=True, text=txtcap, parse_mode='HTML')
                            type_message = "message"
                        elif message.photo:
                            info_msg = bot.send_photo(chat_id=f"@{row_admin['cache']}", photo=message.photo[len(message.photo) - 1].file_id, caption=txtcap, parse_mode='HTML', )
                            type_message = "photo"
                        elif message.video:
                            info_msg = bot.send_video(chat_id=f"@{row_admin['cache']}", video=message.video.file_id, caption=txtcap, parse_mode='HTML', )
                            type_message = "video"
                        elif message.audio:
                            info_msg = bot.send_audio(chat_id=f"@{row_admin['cache']}", audio=message.audio.file_id, parse_mode='HTML', caption=txtcap, )
                            type_message = "audio"
                        elif message.voice:
                            info_msg = bot.send_voice(chat_id=f"@{row_admin['cache']}", voice=message.voice.file_id, caption=txtcap, parse_mode='HTML', )
                            type_message = "voice"
                        elif message.document:
                            info_msg = bot.send_document(chat_id=f"@{row_admin['cache']}", document=message.document.file_id, caption=txtcap, parse_mode='HTML')
                            type_message = "document"
                        else:
                            message.reply_html(text="⛔️ پیام پشتیبانی نمی شود", reply_to_message_id=message_id)
                    except:
                        message.reply_html(text="❌ خطایی در ارتباط با کانال کش رخ داد، کانال را مجدد ثبت کنید و همه دسترسی های ادمین را به ربات بدهید", reply_to_message_id=message_id)
                    cs.execute(
                        f"INSERT INTO {utl.files} (order_id,type_message,message_id,created_at,uniq_id,batch,msg_index) "
                        f"VALUES ({row_orders['id']},'{type_message}',{info_msg.message_id},{timestamp},'{uniq_id}',{batch},{msg_index})"
                    )
                    cs.execute(f"SELECT * FROM {utl.files} WHERE uniq_id='{uniq_id}'")
                    row_files = cs.fetchone()
                    if row_files is None:
                        return message.reply_html(text="❌ خطایی رخ داد، مجدد تلاش کنید", reply_to_message_id=message_id)
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.files} WHERE order_id={row_orders['id']} AND batch={batch}")
                count = cs.fetchone()['count']

                if text != "✅ پایان ✅" and count < 3:
                    next_msg_index = count + 1
                    cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{ex_step[1]};get_message;{batch};{next_msg_index}' WHERE user_id={from_id}")
                    return message.reply_html(
                        text=f"ارسال پیام شماره {next_msg_index} برای بتچ {batch}:\n\n"
                            "❕ حداکثر 3 پیام می توانید ارسال کنید",
                        reply_markup={'resize_keyboard': True,'keyboard': [
                            [{'text': "✅ پایان ✅"}],
                            [{'text': utl.menu_var}]
                        ]}
                    )

                next_batch = batch + 1
                if next_batch <= max_batch:
                    cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{ex_step[1]};get_message;{next_batch};1' WHERE user_id={from_id}")
                    return message.reply_html(
                        text=f"✅ پیام های بتچ {batch} ثبت شد\n\n"
                            f"حالا پیام شماره 1 برای بتچ {next_batch} را ارسال کنید:",
                        reply_markup={'resize_keyboard': True,'keyboard': [
                            [{'text': "✅ پایان ✅"}],
                            [{'text': utl.menu_var}]
                        ]}
                    )

                cs.execute(f"UPDATE {utl.orders} SET status=1 WHERE id={row_orders['id']}")
                cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
                return user_panel(message=message, text=f"✅ سفارش ثبت شد: /order_{row_orders['id']}")
        if text == "➕ ایجاد سفارش":
            cs.execute(f"DELETE FROM {utl.orders} WHERE user_id={from_id} AND status=0")
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE status=1 ORDER BY last_order_at ASC LIMIT 1")
            if cs.fetchone() is None:
                return message.reply_html(text="❌ برای ثبت سفارش باید حداقل یک اکانت فعال داشته باشید", reply_to_message_id=message_id)
            
            uniq_id = utl.unique_id()
            cs.execute(f"INSERT INTO {utl.orders} (user_id,status,status_analyze,created_at,updated_at,uniq_id) VALUES ({from_id},0,0,{timestamp},{timestamp},'{uniq_id}')")
            cs.execute(f"SELECT * FROM {utl.orders} WHERE uniq_id='{uniq_id}'")
            row_orders = cs.fetchone()
            if row_orders is None:
                return message.reply_html(text="❌ خطای ناشناخته، مجدد تلاش کنید", reply_to_message_id=message_id)
            
            cs.execute(f"UPDATE {utl.users} SET step='create_order;{row_orders['id']};category' WHERE user_id={from_id}")
            keyboard = [[{'text': utl.menu_var}, {'text': "⏩ بعدی"}]]
            cs.execute(f"SELECT * FROM {utl.cats}")
            result = cs.fetchall()
            for row in result:
                keyboard.append([{'text': row['name']}])
            return message.reply_html(
                text="یک دسته بندی را انتخاب کنید:",
                reply_markup={'resize_keyboard': True, 'keyboard': keyboard}
            )
        if text == "📋 سفارش ها":
            cs.execute(f"SELECT * FROM {utl.orders} WHERE status>0 ORDER BY id DESC LIMIT 0,{utl.step_page}")
            result = cs.fetchall()
            if not result:
                return message.reply_html(text="❌ لیست خالی است", reply_to_message_id=message_id)
            
            now = jdatetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=3, minutes=30)))
            time_today = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            time_yesterday = time_today - 86400
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.orders}")
            count = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.orders} WHERE created_at>={time_today}")
            orders_count_today = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.orders} WHERE created_at<{time_today} AND created_at>={time_yesterday}")
            orders_count_yesterday = cs.fetchone()['count']

            cs.execute(f"SELECT sum(count_done) FROM {utl.orders} WHERE status=2")
            orders_count_moved_all = cs.fetchone()['sum(count_done)']
            orders_count_moved_all = orders_count_moved_all if orders_count_moved_all is not None else 0
            cs.execute(f"SELECT sum(count_done) FROM {utl.orders} WHERE status=2 AND created_at>={time_today}")
            orders_count_moved_today = cs.fetchone()['sum(count_done)']
            orders_count_moved_today = orders_count_moved_today if orders_count_moved_today is not None else 0
            cs.execute(f"SELECT sum(count_done) FROM {utl.orders} WHERE status=2 AND created_at<{time_today} AND created_at>={time_yesterday}")
            orders_count_moved_yesterday = cs.fetchone()['sum(count_done)']
            orders_count_moved_yesterday = orders_count_moved_yesterday if orders_count_moved_yesterday is not None else 0

            output = f"📋 کل سفارش ها: {count} ({orders_count_moved_all})\n"
            output += f"🟢 سفارش های امروز: {orders_count_today} ({orders_count_moved_today})\n"
            output += f"⚪️ سفارش های دیروز: {orders_count_yesterday} ({orders_count_moved_yesterday})\n\n"
            i = 1
            for row in result:
                group_link = f"<a href='{row['group_link']}'>{row['group_link'].replace('https://t.me/', '')}</a>" if row['group_link'] is not None else "با فایل انجام شده"
                output += f"{i}. جزییات: /order_{row['id']}\n"
                output += f"🔹️ گروه: {group_link}\n"
                output += f"🔹️ انجام شده / درخواستی: [{row['count_done']} / {row['count']}]\n"
                output += f"🔹️ وضعیت: {utl.status_orders[row['status']]}\n"
                output += f"📅️ ایجاد: {jdatetime.datetime.fromtimestamp(row['created_at']).astimezone(datetime.timezone(datetime.timedelta(hours=3, minutes=30))).strftime('%Y/%m/%d %H:%M')}\n\n"
                i += 1
            ob = utl.Pagination(update, "orders", output, utl.step_page, count)
            return ob.process()
        if text == "➕ افزودن اکانت":
            cs.execute(f"DELETE FROM {utl.mbots} WHERE creator_user_id={from_id} AND status=0 AND user_id IS NULL")
            row_apis = utl.select_api(cs, row_admin['api_per_number'])
            if row_apis is None:
                return message.reply_html(text="❌ ابتدا یک API اضافه کنید یا از تنظیمات گزینه اول را افزایش دهید", reply_to_message_id=message_id)
            
            uniq_id = utl.unique_id()
            cs.execute(f"INSERT INTO {utl.mbots} (cat_id,creator_user_id,api_id,api_hash,status,created_at,uniq_id) VALUES (1,{from_id},{row_apis['api_id']},'{row_apis['api_hash']}',0,{timestamp},'{uniq_id}')")
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE uniq_id='{uniq_id}'")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                return message.reply_html(text="❌ خطایی رخ داد، مجدد تلاش کنید")
            
            cs.execute(f"UPDATE {utl.users} SET step='add_acc;{row_mbots['id']};type' WHERE user_id={from_id}")
            return message.reply_html(
                text="روش افزودن اکانت را انتخاب کنید:",
                reply_markup={'resize_keyboard': True,'keyboard': [
                    [{'text': 'زیپ'}, {'text': 'سشن'}, {'text': 'شماره'}],
                    [{'text': utl.menu_var}]
                ]}
            )
        if text == "📋 اکانت ها":
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL")
            accs_all = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL AND status=0")
            accs_logout = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status=1")
            accs_active = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status=2")
            accs_restrict = cs.fetchone()['count']
            return message.reply_html(
                text="📋 اکانت ها\n\n"
                    "❌ محدود شده: اکانت ها بعد از «محدود شدن توسط تلگرام» یا «گزینه سروم تنظیمات» در این وضعیت قرار میگیرند و بعد از تمام محدودیت خودکار از این حالت خارج می شوند\n\n"
                    "⛔️ لاگ اوت شده: اکانت هایی که لاگ اوت یا توسط تلگرام بن شده اند\n\n"
                    "✅ فعال: اکانت هایی که در ربات لاگین و قابل استفاده هستند",
                reply_markup={'inline_keyboard': [
                    [{'text': f"💢 همه ({accs_all}) 💢", 'callback_data': f"pg;accounts;1"}],
                    [
                        {'text': f"⛔️ لاگ اوت شده ({accs_logout})", 'callback_data': f"pg;0;1"},
                        {'text': f"❌ محدود شده ({accs_restrict})", 'callback_data': f"pg;2;1"}
                    ],
                    [{'text': f"✅ فعال ({accs_active})", 'callback_data': f"pg;1;1"}],
                    [{'text': "👇 دستورات عمومی 👇", 'callback_data': "nazan"}],
                    [{'text': "✔️ حذف لاگ اوت شده ها ✔️", 'callback_data': "gc;1"}],
                ]}
            )
        if text == "➕ افزودن API":
            cs.execute(f"UPDATE {utl.users} SET step='add_api;' WHERE user_id={from_id}")
            return message.reply_html(
                text="‏ API را مطابق نمونه ارسال کنید:\n\n"
                    "مثال:\n"
                    "‏api id (در خط اول)\n"
                    "‏api hash (در خط دوم)",
                reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
            )
        if text == "‏📋 API ها":
            cs.execute(f"SELECT * FROM {utl.apis} ORDER BY id DESC LIMIT 0,{utl.step_page}")
            result = cs.fetchall()
            if not result:
                return message.reply_html(text="❌ لیست API خالی است", reply_to_message_id=message_id)
            
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.apis}")
            rowcount = cs.fetchone()['count']
            output = f"‏📜 API ها ({rowcount})\n\n"
            for row in result:
                output += f"‏🔴️ Api ID: ‏<code>{row['api_id']}</code>\n"
                output += f"‏🔴️ Api Hash: ‏<code>{row['api_hash']}</code>\n"
                output += f"❌ حذف: /DeleteApi_{row['id']}\n\n"
            ob = utl.Pagination(update, "apis", output, utl.step_page, rowcount)
            return ob.process()
        if text == "➕ ایجاد دسته بندی":
            cs.execute(f"UPDATE {utl.users} SET step='create_cat;none' WHERE user_id={from_id}")
            return message.reply_html(
                text="نام دسته بندی را وارد کنید:",
                reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
            )
        if text == "📋 دسته بندی ها":
            cs.execute(f"SELECT * FROM {utl.cats} ORDER BY id DESC LIMIT 0,{utl.step_page}")
            result = cs.fetchall()
            if not result:
                return message.reply_html(text="❌ لیست خالی است", reply_to_message_id=message_id)
            
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.cats}")
            rowcount = cs.fetchone()['count']
            output = f"📋 دسته بندی ها ({rowcount})\n\n"
            i = 1
            for row in result:
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE cat_id={row['id']}")
                count_mbots = cs.fetchone()['count']
                output += f"{i}. ‏{row['name']} ‏({count_mbots} اکانت)\n"
                output += f"❌ حذف: /DeleteCat_{row['id']}\n\n"
                i += 1
            ob = utl.Pagination(update, "categories", output, utl.step_page, rowcount)
            return ob.process()
        if text == "🔮 آنالیز":
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                return message.reply_html(text="❌ هیچ اکانتی یافت نشد", reply_to_message_id=message_id)
            
            cs.execute(f"UPDATE {utl.users} SET step='analyze;type' WHERE user_id={from_id}")
            return message.reply_html(
                text="نوع آنالیز را انتخاب کنید:",
                reply_markup={'resize_keyboard': True,'keyboard': [
                    [{'text': 'پیام ها'}, {'text': 'کاربران'}],
                    [{'text': utl.menu_var}],
                ]}
            )
        if text == "⚙️ تنظیمات":
            return message.reply_html(
                text="⚙️ تنظیمات",
                reply_markup={'inline_keyboard': [
                    [{'text': f"📝 در هر API چند اکانت ثبت شود: {row_admin['api_per_number']} اکانت",'callback_data': "settings;api_per_number"}],
                    [{'text': f"📝 ارسال هر اکانت در هر استفاده: {row_admin['send_per_h']} ارسال",'callback_data': "settings;send_per_h"}],
                    [{'text': (f"📝 استفاده اکانت هر چند ساعت: " + (f"{int(row_admin['limit_per_h'] / 3600)} ساعت" if row_admin['limit_per_h'] > 0 else "غیرفعال ❌")),'callback_data': "settings;limit_per_h"}],
                    [{'text': f"🔐 رمز دو مرحله ای: " + (row_admin['account_password'] if row_admin['account_password'] is not None else "ثبت نشده") + "",'callback_data': "settings;account_password"}],
                    [{'text': ("تنظیم / تغییر رمز دو مرحله ای: " + ("فعال ✅" if row_admin['change_pass'] > 0 else "غیرفعال ❌")),'callback_data': "settings;change_pass"}],
                    [{'text': ("خروج از بقیه سشن ها: " + ("فعال ✅" if row_admin['exit_session'] > 0 else "غیرفعال ❌")),'callback_data': "settings;exit_session"}],
                    [{'text': ("تنظیم نام، بیو و پروفایل: " + ("فعال ✅" if row_admin['is_change_profile'] > 0 else "غیرفعال ❌")),'callback_data': "settings;is_change_profile"}],
                    [{'text': ("تنظیم یوزرنیم: " + ("فعال ✅" if row_admin['is_set_username'] > 0 else "غیرفعال ❌")),'callback_data': "settings;is_set_username"}],
                ]}
            )
        if text == "👤 کاربر":
            cs.execute(f"UPDATE {utl.users} SET step='info_user;' WHERE user_id={from_id}")
            return message.reply_html(
                text="آیدی عددی کاربر را ارسال کنید:\n\n"
                    "❕ برای بدست آوردن آیدی عددی می توانید از ربات @info_tel_bot استفاده کنید",
                reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
            )
        if ex_text[0] == '/order':
            cs.execute(f"SELECT * FROM {utl.orders} WHERE id={int(ex_text[1])}")
            row_orders = cs.fetchone()
            if row_orders is None:
                return message.reply_html(text="❌ سفارش یافت نشد")
            
            if row_orders['group_link'] is not None:
                output = f"\n🆔 <code>{row_orders['group_id']}</code>\n"
                output += f"🔗 {row_orders['group_link']}\n\n"
            else:
                output = "از طریق لیست انجام شده\n\n"
            if row_orders['cats'] is None:
                cats = "پشتیبانی نمی شود"
            else:
                where = ""
                cats = row_orders['cats'].split(",")
                for category in cats:
                    where += f"id={int(category)} OR "
                where = where[0:-4]
                cats = ""
                cs.execute(f"SELECT * FROM {utl.cats} WHERE {where}")
                result = cs.fetchall()
                for row in result:
                    cats += f"{row['name']},"
                cats = cats[0:-1]
            return message.reply_html(
                text=f"اطلاعات گروه: {output}"
                    f"👤 ارسال شده / درخواستی: [{row_orders['count_done']:,} / {row_orders['count']:,}]\n"
                    f"👤 در حال بررسی / همه: [{row_orders['count_request']:,} / {row_orders['max_users']:,}]\n\n"
                    f"🔵 گزارش اکانت ها\n"
                    f"      استفاده شده: {row_orders['count_acc']:,}\n"
                    f"      محدود شده: {row_orders['count_restrict']:,}\n"
                    f"      ریپورت شده: {row_orders['count_report']:,}\n"
                    f"      از دست رفته: {row_orders['count_accout']:,}\n\n"
                    f"🔴 گزارش درخواست های ارسال\n"
                    f"      خطا های اسپم: {row_orders['count_usrspam']:,}\n"
                    f"      یوزرنیم اشتباه: {row_orders['count_userincorrect']:,}\n"
                    f"      اکانت های محدود: {row_orders['count_restrict_error']:,}\n"
                    f"      خطا های دیگر: {row_orders['count_other_errors']:,}\n\n"
                    f"🟣 دسته بندی ها: {cats}\n"
                    f"🟣 تعداد ارسال هر اکانت: {row_orders['send_per_h']:,}\n\n"
                    f"📥 خروجی کاربران باقی مانده: /exo_{row_orders['id']}_r\n"
                    f"📥 خروجی کاربران منتقل شده: /exo_{row_orders['id']}_m\n"
                    "➖➖➖➖➖➖\n"
                    f"📅️ ایجاد: {jdatetime.datetime.fromtimestamp(row_orders['created_at']).astimezone(datetime.timezone(datetime.timedelta(hours=3, minutes=30))).strftime('%Y/%m/%d %H:%M:%S')}\n"
                    f"📅️ بروزرسانی: {jdatetime.datetime.fromtimestamp(row_orders['updated_at']).astimezone(datetime.timezone(datetime.timedelta(hours=3, minutes=30))).strftime('%Y/%m/%d %H:%M:%S')}\n"
                    f"📅 الان: {jdatetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=3, minutes=30))).strftime('%Y/%m/%d %H:%M:%S')}",
                reply_markup={'inline_keyboard': [
                    [{'text': utl.status_orders[row_orders['status']], 'callback_data': (f"change_status;{row_orders['id']};2" if row_orders['status'] == 1 else "nazan")}],
                    [{'text': '🔄 بروزرسانی 🔄', 'callback_data': f"update;{row_orders['id']}"}]
                ]}
            )
        if ex_text[0] == '/category':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_text[1])}")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                return message.reply_html(text="❌ اکانت یافت نشد", reply_to_message_id=message_id)
            
            cs.execute(f"UPDATE {utl.users} SET step='set_cat;{row_mbots['id']}' WHERE user_id={from_id}")
            keyboard = []
            cs.execute(f"SELECT * FROM {utl.cats}")
            result = cs.fetchall()
            for row in result:
                keyboard.append([{'text': row['name']}])
            keyboard.append([{'text': utl.menu_var}])
            return message.reply_html(
                text="یکی از دسته بندی ها را انتخاب کنید:",
                reply_markup={'resize_keyboard': True,'keyboard': keyboard}
            )
        if ex_text[0] == '/DeleteCat':
            cs.execute(f"SELECT * FROM {utl.cats} WHERE id={int(ex_text[1])}")
            row_cats = cs.fetchone()
            if row_cats is None:
                return message.reply_html(text="❌ دسته بندی یافت نشد", reply_to_message_id=message_id)
            if row_cats['id'] == 1:
                return message.reply_html(text="❌ دسته بندی قابل حذف نیست")
            
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE cat_id={row_cats['id']}")
            count = cs.fetchone()['count']
            if count < 1:
                cs.execute(f"DELETE FROM {utl.cats} WHERE id={row_cats['id']}")
                return message.reply_html(text="✅ با موفقیت حذف شد", reply_to_message_id=message_id)
            
            return message.reply_html(
                text=f"❌ حذف دسته بندی: {row_cats['name']}\n\n"
                    f"/DeleteCatConfirm_{row_cats['id']}\n\n"
                    f"⚠️ {count} اکانت در این دسته بندی ثبت شده است",
                reply_to_message_id=message_id
            )
        if ex_text[0] == '/DeleteCatConfirm':
            cs.execute(f"SELECT * FROM {utl.cats} WHERE id={int(ex_text[1])}")
            row_cats = cs.fetchone()
            if row_cats is None:
                return message.reply_html(text="❌ دسته بندی یافت نشد", reply_to_message_id=message_id)
            if row_cats['id'] == 1:
                return message.reply_html(text="❌ دسته بندی قابل حذف نیست")
            
            cs.execute(f"UPDATE {utl.mbots} SET cat_id=1 WHERE cat_id={row_cats['id']}")
            cs.execute(f"DELETE FROM {utl.cats} WHERE id={row_cats['id']}")
            return message.reply_html(text="✅ با موفقیت حذف شد", reply_to_message_id=message_id)
        if ex_text[0] == '/status':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_text[1])}")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                return message.reply_html(text="❌ اکانت یافت نشد", reply_to_message_id=message_id)
            
            info_msg = message.reply_html(text="در حال اتصال ...", reply_to_message_id=message_id)
            return os.system(f"{utl.python_version} \"{directory}/tl_account_status.py\" {row_mbots['uniq_id']} {from_id} {info_msg.message_id}")
        if ex_text[0] == '/delete':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_text[1])}")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                return message.reply_html(text="❌ اکانت یافت نشد", reply_to_message_id=message_id)
            
            return message.reply_html(
                text=f"❌ حذف اکانت: <code>{row_mbots['phone']}</code>\n\n"
                    f"/deleteconfirm_{ex_text[1]}",
                reply_to_message_id=message_id
            )
        if ex_text[0] == '/deleteconfirm':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_text[1])}")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                return message.reply_html(text="❌ اکانت یافت نشد", reply_to_message_id=message_id)
            
            cs.execute(f"DELETE FROM {utl.mbots} WHERE id={row_mbots['id']}")
            return message.reply_html(text=f"‏✅ اکانت <code>{row_mbots['phone']}</code> با موفقیت حذف شد", reply_to_message_id=message_id)
        if ex_text[0] == '/DeleteApi':
            cs.execute(f"SELECT * FROM {utl.apis} WHERE id={int(ex_text[1])}")
            row_apis = cs.fetchone()
            if row_apis is None:
                return message.reply_html(text="‏❌ API یافت نشد", reply_to_message_id=message_id)
            
            cs.execute(f"DELETE FROM {utl.apis} WHERE id={row_apis['id']}")
            return message.reply_html(text="‏✅ API با موفقیت حذف شد", reply_to_message_id=message_id)
        if ex_text[0] == '/ex':
            cs.execute(f"SELECT * FROM {utl.egroup} WHERE id={int(ex_text[1])}")
            row_egroup = cs.fetchone()
            if row_egroup is None:
                return message.reply_html(text="❌ سفارش یافت نشد", reply_to_message_id=message_id)
            if row_egroup['type'] == 0:
                info_msg = message.reply_html(text="در حال ارسال ...")
                try:
                    if ex_text[2] == 'a':
                        message.reply_document(document=open(f"{directory}/export/{row_egroup['id']}/users_all.txt","rb"), caption="همه کاربران", reply_to_message_id=message_id)
                    elif ex_text[2] == 'u':
                        message.reply_document(document=open(f"{directory}/export/{row_egroup['id']}/users_real.txt","rb"), caption="کاربران واقعی", reply_to_message_id=message_id)
                    elif ex_text[2] == 'f':
                        message.reply_document(document=open(f"{directory}/export/{row_egroup['id']}/users_fake.txt","rb"), caption="کاربران فیک", reply_to_message_id=message_id)
                    elif ex_text[2] == 'n':
                        message.reply_document(document=open(f"{directory}/export/{row_egroup['id']}/users_has_phone.txt","rb"), caption="کاربران با شماره", reply_to_message_id=message_id)
                    elif ex_text[2] == 'o':
                        message.reply_document(document=open(f"{directory}/export/{row_egroup['id']}/users_online.txt","rb"), caption="کربران آنلاین", reply_to_message_id=message_id)
                except:
                    return info_msg.edit_text(text="❌ خطایی در ارسال فایل رخ داد")
                return info_msg.delete()
            else:
                info_msg = message.reply_html(text="در حال ارسال ...")
                try:
                    if ex_text[2] == 'a':
                        message.reply_document(document=open(f"{directory}/export/{row_egroup['id']}/users_all.txt","rb"), caption='کاربارن شناسایی شده', reply_to_message_id=message_id)
                    elif ex_text[2] == 'u':
                        message.reply_document(document=open(f"{directory}/export/{row_egroup['id']}/users_username.txt","rb"), caption="کاربران با یوزرنیم", reply_to_message_id=message_id)
                    elif ex_text[2] == 'b':
                        message.reply_document(document=open(f"{directory}/export/{row_egroup['id']}/users_bots.txt","rb"), caption="ربات ها", reply_to_message_id=message_id)
                except:
                    message.reply_html(text="❌ There was a problem uploading the file")
                return info_msg.delete()
        if ex_text[0] == '/exo':
            cs.execute(f"SELECT * FROM {utl.orders} WHERE id={int(ex_text[1])}")
            row_orders = cs.fetchone()
            if row_orders is None:
                return message.reply_html(text="❌ سفارش یافت نشد", reply_to_message_id=message_id)
            if row_orders['status'] != 2:
                return message.reply_html(text="❌ سفارش هنوز تمام نشده است", reply_to_message_id=message_id)
            
            info_msg = message.reply_html(text="در حال ارسال ...")
            if ex_text[2] == 'm':
                if not os.path.exists(f"{directory}/files/exo_{row_orders['id']}_m.txt"):
                    return message.reply_html(text="❌ هیچ ممبری یافت نشد", reply_to_message_id=message_id)
                message.reply_document(document=open(f"{directory}/files/exo_{row_orders['id']}_m.txt", "rb"), caption="کاربران منتقل شده", reply_to_message_id=message_id)
            elif ex_text[2] == 'r':
                if not os.path.exists(f"{directory}/files/exo_{row_orders['id']}_r.txt"):
                    return message.reply_html(text="❌ هیچ ممبری یافت نشد", reply_to_message_id=message_id)
                message.reply_document(document=open(f"{directory}/files/exo_{row_orders['id']}_r.txt", "rb"), caption="کاربران باقی مانده", reply_to_message_id=message_id)
            return info_msg.delete()
        

if __name__ == '__main__':
    updater = telegram.ext.Updater(utl.token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.chat_type.private & telegram.ext.Filters.update.message & telegram.ext.Filters.update, private_process, run_async=True))
    dispatcher.add_handler(telegram.ext.CallbackQueryHandler(callbackquery_process, run_async=True))
    
    updater.start_polling()
    updater.idle()
