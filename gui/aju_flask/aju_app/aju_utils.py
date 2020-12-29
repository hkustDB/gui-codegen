import os
import json
import subprocess
import logging

import aju_app
import config


def is_json_file(the_file):
    with open(the_file, 'r') as f:
        data = f.read()
    try:
        json_obj = json.loads(data)
    except ValueError:
        return False
    return True


def run_flink_task(filename, query_idx):

    from config import REMOTE_FLINK
    from config import REMOTE_FLINK_URL

    if filename == '':
        ret = subprocess.CompletedProcess(args='', returncode=1, stdout="filename is null.")
        return ret

    generated_jar_file_path = os.path.join(config.GENERATED_JAR_PATH, filename)
    if not os.path.exists(generated_jar_file_path):
        ret = subprocess.CompletedProcess(args='', returncode=1, stdout="generated jar does not exist.")
        return ret

    generated_jar_para = ""
    flink_command_path = os.path.join(config.FLINK_HOME_PATH, "bin/flink")
    if REMOTE_FLINK:
        cmd_str = flink_command_path + " run " + " -m " + REMOTE_FLINK_URL + " " + generated_jar_file_path + " " + generated_jar_para
    else:
        cmd_str = flink_command_path + " run " + generated_jar_file_path + " " + generated_jar_para

    logging.info("flink command: " + cmd_str)

    ret = subprocess.run(cmd_str, shell=True, capture_output=True)
    result = str(ret.stdout) + str('\n') + str(ret.stderr)
    logging.info('flink jobs return: ' + result)
    # aju_app.background_send_kafka_data_thread(query_idx)
    aju_app.send_query_result_data_to_client(query_idx)
    return ret


def run_codegen_to_generate_jar(uploaded_json_file_save_path, query_idx):
    if query_idx == 3:
        cmd_str = 'java -jar' + ' ' \
                  + config.CODEGEN_FILE + ' ' \
                  + uploaded_json_file_save_path + ' ' \
                  + config.GENERATED_JAR_PATH + ' ' \
                  + 'file://' + config.Q3_INPUT_DATA_FILE + ' ' \
                  + 'file://' + config.Q3_OUTPUT_DATA_FILE + ' ' + 'file'
        logging.info("Q3: ")
    elif query_idx == 6:
        cmd_str = 'java -jar' + ' ' \
                  + config.CODEGEN_FILE + ' ' \
                  + uploaded_json_file_save_path + ' ' \
                  + config.GENERATED_JAR_PATH + ' ' \
                  + 'file://' + config.Q6_INPUT_DATA_FILE + ' ' \
                  + 'file://' + config.Q6_OUTPUT_DATA_FILE + ' ' + 'file'
        logging.info("Q6: ")
    else:
        logging.error("query index is not supported.")
        raise Exception("query index is not supported.")

    logging.info("codegen command: " + cmd_str)
    ret = subprocess.run(cmd_str, shell=True, capture_output=True)

    codegen_log_stdout = str(ret.stdout, encoding="utf-8") + "\n"
    codegen_log_stderr = str(ret.stderr, encoding="utf-8") + "\n"
    codegen_log_result = codegen_log_stdout + codegen_log_stderr
    with open("./log/codegen.log", "w") as f:
        f.write(codegen_log_result)

    # remove the uploaded file
    if os.path.exists(uploaded_json_file_save_path):
        os.remove(uploaded_json_file_save_path)

    logging.info('codegen_log_result: ' + codegen_log_result)
    return codegen_log_result, ret.returncode


def is_flink_cluster_running():
    from config import REMOTE_FLINK
    if REMOTE_FLINK:
        # TODO
        pass
    else:
        cmd_str = 'jps|grep Cluster'
        ret = subprocess.run(cmd_str, shell=True, capture_output=True)
        if ret.returncode == 0:
            return True
        else:
            return False


def get_query_idx(filename):
    if filename.split('.')[1] == "json":
        query = filename.split('.')[0]
        if query[0] == 'Q':
            return int(query[1:])
    return 0


def send_notify_of_start_to_run_flink_job():
    print('start_to_run_flink_job')
    aju_app.socketio.send('start_to_run_flink_job', {'data': 1})


def clean_codegen_log_and_generated_jar():
    if os.path.exists(config.CODEGEN_LOG_FILE):
        os.remove(config.CODEGEN_LOG_FILE)
    if os.path.exists(config.GENERATED_JAR_FILE):
        os.remove(config.GENERATED_JAR_FILE)