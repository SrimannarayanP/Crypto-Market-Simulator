# driver.py


import threading, subprocess

# Threading allows multiple tasks to run concurrently
# subprocess allows us to spawn new commands & run external commands


def run_script(script_name):

    subprocess.run(['python', script_name])

# run_script is used to run a Python script as if you typed it in cmd.


fetch_real_time_data_thread = threading.Thread(target = run_script, args = ('fetch_real_time_data.py',)) # Basically calls the run_script func., passing the file name as a param
execute_update_trades_thread = threading.Thread(target = run_script, args = ('execute_update_trades.py',))
graph_server_thread = threading.Thread(target = run_script, args = ('graph_server.py',))
# pygame_ui_thread = threading.Thread(target = run_script , args = ('ui.py',))  # New thread for the Pygame UI

fetch_real_time_data_thread.start() # Starts all 3 threads, allowing 3 diff. scripts to run concurrently
execute_update_trades_thread.start()
graph_server_thread.start()
# pygame_ui_thread.start()

fetch_real_time_data_thread.join() # Makes the main program wait until it ensures that all the threads' execution has been completed
execute_update_trades_thread.join()
graph_server_thread.join()
# pygame_ui_thread.join()
