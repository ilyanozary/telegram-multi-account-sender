import os, time, utility as utl


directory = os.path.dirname(os.path.abspath(__file__))
filename = str(os.path.basename(__file__))

utl.get_params_pids_by_full_script_name(script_names=[f"{directory}/{filename}"], is_kill_proccess=True)
print(f"ok: {filename}")


while True:
    try:
        timestamp = int(time.time())
        cs = utl.Database()
        cs = cs.data()

        cs.execute(f"SELECT * FROM {utl.admin}")
        row_admin = cs.fetchone()

        cs.execute(f"SELECT * FROM {utl.orders} WHERE status=1")
        row_orders = cs.fetchone()
        if row_orders is not None:
            where = ""
            cats = row_orders['cats'].split(",")
            for category in cats:
                where += f"cat_id={int(category)} OR "
            where = where[0:-4]
            
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE status=1 AND ({where}) ORDER BY last_order_at ASC")
            result_mbots = cs.fetchall()
            if result_mbots:
                for row_mbots in result_mbots:
                    result_pids = utl.get_params_pids_by_full_script_name(param1=row_mbots['uniq_id'])
                    if not result_pids:
                        cs.execute(f"SELECT * FROM {utl.usedaccs} WHERE order_id={row_orders['id']} AND bot_id={row_mbots['id']}")
                        if cs.fetchone() is None:
                            os.system(f"{utl.python_version} \"{directory}/tl_run_account.py\" {row_mbots['uniq_id']} {row_orders['id']}")
                        
                        cs.execute(f"SELECT * FROM {utl.orders} WHERE id={row_orders['id']}")
                        row_orders = cs.fetchone()
                        if row_orders['status'] == 2:
                            break
            
            cs.execute(f"SELECT * FROM {utl.orders} WHERE id={row_orders['id']}")
            row_orders = cs.fetchone()
            if row_orders['status'] != 2:
                utl.end_order(cs, f"{directory}/files/exo_{row_orders['id']}_r.txt", row_orders)
    except Exception as e:
        print(f"Error in main: {e}")
    time.sleep(10)

