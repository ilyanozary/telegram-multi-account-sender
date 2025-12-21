import os, re, sys, time, datetime, telethon, telethon.sync, utility as utl


for index, arg in enumerate(sys.argv):
    if index == 1:
        mbots_uniq_id = arg
    elif index == 2:
        order_id = int(arg)

directory = os.path.dirname(os.path.abspath(__file__))
filename = str(os.path.basename(__file__))

cs = utl.Database()
cs = cs.data()

cs.execute(f"SELECT * FROM {utl.admin}")
row_admin = cs.fetchone()
cs.execute(f"SELECT * FROM {utl.orders} WHERE id={order_id}")
row_orders = cs.fetchone()
cs.execute(f"SELECT * FROM {utl.mbots} WHERE uniq_id='{mbots_uniq_id}'")
row_mbots = cs.fetchone()

utl.get_params_pids_by_full_script_name(script_names=[f"{directory}/{filename}"], param1=row_mbots["uniq_id"], is_kill_proccess=True)


def check_report(client):
    try:
        for r in client(telethon.functions.messages.StartBotRequest(bot="@spambot", peer="@spambot", start_param="start")).updates:
            time.sleep(1)
            for r1 in client(telethon.functions.messages.GetMessagesRequest(id=[r.id + 1])).messages:
                if "I’m afraid some Telegram users found your messages annoying and forwarded them to our team of moderators for inspection." in r1.message:
                    if "Unfortunately, your account is now limited" in r1.message:
                        return int(time.time()) + 604800
                    else:
                        regex = re.findall('automatically released on [\d\w ,:]*UTC', r1.message)[0]
                        date_str = regex.replace("automatically released on ","")
                        utc_time = datetime.datetime.strptime(date_str, '%d %b %Y, %H:%M %Z')
                        timestamp = utc_time.replace(tzinfo=datetime.timezone.utc).timestamp()
                        return int(timestamp)
                elif "While the account is limited, you will not be able to send messages to people who do not have your number in their phone contacts" in r1.message:
                    return int(time.time()) + 604800
            break
    except:
        pass
    return False


def operation(cs, row_orders, row_mbots, result):
    try:
        count_send = i = 0
        cs.execute(f"SELECT COUNT(*) as count FROM {utl.reports} WHERE order_id={row_orders['id']} AND status=1")
        total_send = cs.fetchone()['count']
        if total_send > 0 and total_send >= row_orders['count']:
            return utl.end_order(cs, f"{directory}/files/exo_{row_orders['id']}_r.txt", row_orders)
        
        cs.execute(f"INSERT INTO {utl.usedaccs} (order_id,bot_id,created_at) VALUES ({row_orders['id']},{row_mbots['id']},{int(time.time())})")
        cs.execute(f"UPDATE {utl.mbots} SET last_order_at={int(time.time())} WHERE id={row_mbots['id']}")
        cs.execute(f"UPDATE {utl.orders} SET count_acc=count_acc+1,updated_at={int(time.time())} WHERE id={row_orders['id']}")

        client = telethon.sync.TelegramClient(session=f"{directory}/sessions/{row_mbots['uniq_id']}", api_id=row_mbots['api_id'], api_hash=row_mbots['api_hash'])
        client.connect()
        if not client.is_user_authorized():
            cs.execute(f"UPDATE {utl.mbots} SET status=0 WHERE id={row_mbots['id']}")
            cs.execute(f"UPDATE {utl.orders} SET count_accout=count_accout+1 WHERE id={row_orders['id']}")
            return print(f"{row_mbots['id']}: Log Out")
        
        restrict = check_report(client)
        if restrict:
            cs.execute(f"UPDATE {utl.mbots} SET status=2,end_restrict={restrict} WHERE id={row_mbots['id']}")
            cs.execute(f"UPDATE {utl.orders} SET count_report=count_report+1 WHERE id={row_orders['id']}")
            return print(f"{row_mbots['id']}: Limited")
        
        limit_per_h = int(time.time()) + row_admin['limit_per_h']
        cs.execute(f"UPDATE {utl.mbots} SET status=2,end_restrict={limit_per_h} WHERE id={row_mbots['id']}")
        while count_send < row_orders['send_per_h']:
            cs.execute(f"SELECT MIN(batch) as batch FROM {utl.analyze} WHERE order_id={row_orders['id']}")
            current_batch = cs.fetchone()['batch']
            if current_batch is None:
                break
            current_batch = int(current_batch)

            msgs = []
            cs.execute(f"SELECT * FROM {utl.files} WHERE order_id={row_orders['id']} AND batch={current_batch} ORDER BY msg_index ASC")
            result_plus = cs.fetchall()
            for row_pus in result_plus:
                msgs.append(client.get_messages(f"@{row_admin['cache']}", ids=row_pus['message_id']))

            remaining = row_orders['send_per_h'] - count_send
            cs.execute(
                f"SELECT * FROM {utl.analyze} "
                f"WHERE order_id={row_orders['id']} AND batch={current_batch} "
                f"LIMIT {remaining}"
            )
            result_batch = cs.fetchall()
            if not result_batch:
                break

            for row in result_batch:
                cs.execute(f"UPDATE {utl.orders} SET count_request=count_request+1 WHERE id={row_orders['id']}")
                cs.execute(f"DELETE FROM {utl.analyze} WHERE username='{row['username']}'")
                try:
                    for message in msgs:
                        if message.media is None:
                            client.send_message(entity=row['username'], message=message, parse_mode='html') 
                        else:
                            client.send_file(entity=row['username'], file=message, caption=message.message, parse_mode='html') 
                    cs.execute(f"UPDATE {utl.orders} SET count_done=count_done+1 WHERE id={row_orders['id']}")
                    utl.insert(cs, f"INSERT INTO {utl.reports} (order_id,bot_id,user_id,username,group_id,status,created_at) VALUES ({row_orders['id']},{row_mbots['id']},{row['user_id']},'{row['username']}','{row_orders['group_id']}',1,{int(time.time())})")
                    print(f"{row_mbots['id']} ({i}): Send")
                    count_send += 1
                    if (total_send + count_send) >= row_orders['count']:
                        return
                    if count_send >= row_orders['send_per_h']:
                        return
                except telethon.errors.FloodWaitError as e:
                    print(f"{row_mbots['id']} ({i}): Restricted when Send")
                    end_restrict = int(time.time()) + int(e.seconds)
                    if end_restrict > limit_per_h:
                        cs.execute(f"UPDATE {utl.mbots} SET status=2,end_restrict={end_restrict} WHERE id={row_mbots['id']}")
                    return cs.execute(f"UPDATE {utl.orders} SET count_restrict=count_restrict+1,count_restrict_error=count_restrict_error+1 WHERE id={row_orders['id']}")
                except Exception as e:
                    error = str(e)
                    print(f"{row_mbots['id']} ({i}): Error when Send: {e}")
                    if 'Too many requests' in error:
                        cs.execute(f"UPDATE {utl.orders} SET count_usrspam=count_usrspam+1 WHERE id={row_orders['id']}")
                    elif 'No user has' in error or 'The specified user was deleted' in error or 'ResolveUsernameRequest' in error:
                        cs.execute(f"UPDATE {utl.orders} SET count_userincorrect=count_userincorrect+1 WHERE id={row_orders['id']}")
                    elif 'You can\'t write in this chat' in error:
                        cs.execute(f"UPDATE {utl.orders} SET count_restrict_error=count_restrict_error+1 WHERE id={row_orders['id']}")
                    else:
                        cs.execute(f"UPDATE {utl.orders} SET count_other_errors=count_other_errors+1 WHERE id={row_orders['id']}")
                i += 1
                if i % 3 == 0:
                    time.sleep(1)
    except Exception as e:
        print(f"{row_mbots['id']}: Error when Start: {e}")
    finally:
        try:
            client.disconnect()
        except:
            pass
    print(f"{row_mbots['id']}: RESULT: [{count_send} / {total_send}]")

if row_orders is not None and row_mbots is not None:
    cs.execute(f"SELECT * FROM {utl.analyze} WHERE order_id={row_orders['id']} LIMIT 1")
    if cs.fetchone() is not None:
        operation(cs, row_orders, row_mbots, [])
    else:
        utl.end_order(cs, f"{directory}/files/exo_{row_orders['id']}_r.txt", row_orders)