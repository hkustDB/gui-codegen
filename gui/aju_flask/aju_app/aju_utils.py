import os
import json
import subprocess
import logging

import aju_app
from config import BaseConfig


def is_json_file(the_file):
    with open(the_file, 'r') as f:
        data = f.read()
    try:
        json_obj = json.loads(data)
    except ValueError:
        return False
    return True


def run_flink_task(filename, query_idx):

    if filename == '':
        ret = subprocess.CompletedProcess(args='', returncode=1, stdout="filename is null.")
        return ret

    generated_jar_file_path = os.path.join(BaseConfig.GENERATED_JAR_PATH, filename)
    if not os.path.exists(generated_jar_file_path):
        ret = subprocess.CompletedProcess(args='', returncode=1, stdout="generated jar does not exist.")
        return ret

    generated_jar_para = ""
    flink_command_path = os.path.join(BaseConfig.FLINK_HOME_PATH, "bin/flink")
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
                  + BaseConfig.CODEGEN_FILE + ' ' \
                  + uploaded_json_file_save_path + ' ' \
                  + BaseConfig.GENERATED_JAR_PATH + ' ' \
                  + 'file://' + BaseConfig.Q3_INPUT_DATA_FILE + ' ' \
                  + 'file://' + BaseConfig.Q3_OUTPUT_DATA_FILE + ' ' + 'file'
        logging.info("Q3: ")
    elif query_idx == 6:
        cmd_str = 'java -jar' + ' ' \
                  + BaseConfig.CODEGEN_FILE + ' ' \
                  + uploaded_json_file_save_path + ' ' \
                  + BaseConfig.GENERATED_JAR_PATH + ' ' \
                  + 'file://' + BaseConfig.Q6_INPUT_DATA_FILE + ' ' \
                  + 'file://' + BaseConfig.Q6_OUTPUT_DATA_FILE + ' ' + 'file'
        logging.info("Q6: ")
    elif query_idx == 10:
        cmd_str = 'java -jar' + ' ' \
                  + BaseConfig.CODEGEN_FILE + ' ' \
                  + uploaded_json_file_save_path + ' ' \
                  + BaseConfig.GENERATED_JAR_PATH + ' ' \
                  + 'file://' + BaseConfig.Q10_INPUT_DATA_FILE + ' ' \
                  + 'file://' + BaseConfig.Q10_OUTPUT_DATA_FILE + ' ' + 'file'
        logging.info("Q10: ")
    elif query_idx == 18:
        cmd_str = 'java -jar' + ' ' \
                  + BaseConfig.CODEGEN_FILE + ' ' \
                  + uploaded_json_file_save_path + ' ' \
                  + BaseConfig.GENERATED_JAR_PATH + ' ' \
                  + 'file://' + BaseConfig.Q18_INPUT_DATA_FILE + ' ' \
                  + 'file://' + BaseConfig.Q18_OUTPUT_DATA_FILE + ' ' + 'file'
        logging.info("Q18: ")
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

    # aju_app.r_send_codgen_log_and_retcode(codegen_log_result, ret.returncode)
    return codegen_log_result, ret.returncode


def r_run_codegen_to_generate_jar(json_file_path, query_idx):
    if query_idx == 3:
        cmd_str = 'java -jar' + ' ' \
                  + BaseConfig.CODEGEN_FILE + ' -j ' \
                  + json_file_path + ' -g ' \
                  + BaseConfig.GENERATED_JAR_PATH + ' -i ' \
                  + 'file://' + BaseConfig.Q3_INPUT_DATA_FILE + ' -o ' \
                  + 'file://' + BaseConfig.Q3_OUTPUT_DATA_FILE + ' -s ' + 'file socket'
        logging.info("Q3: ")
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
    logging.info('codegen_log_result: ' + codegen_log_result)
    return codegen_log_result, ret.returncode

def is_flink_cluster_running():
    from config import BaseConfig
    if BaseConfig.REMOTE_FLINK:
        # TODO
        pass
    else:
        cmd_str = 'jps|grep Cluster'
        ret = subprocess.run(cmd_str, shell=True, capture_output=True)
        if ret.returncode == 0:
            return True
        else:
            return False


def kill_5001_port():
    ret = subprocess.run("lsof -i tcp:5001", shell=True, capture_output=True)
    content = str(ret.stdout, 'utf-8')
    if not content:
        print("5001 port is available.")
        return
    try:
        port_pid_str = content.splitlines()[1].split(' ')[1]
    except IndexError:
        print("can not find the pid of port 5001.")
        return
    ret = subprocess.run("kill " + port_pid_str, shell=True, capture_output=True)
    if ret.returncode == 0:
        print("kill 5001 successfully.")


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
    if os.path.exists(BaseConfig.CODEGEN_LOG_FILE):
        os.remove(BaseConfig.CODEGEN_LOG_FILE)
    if os.path.exists(BaseConfig.GENERATED_JAR_FILE):
        os.remove(BaseConfig.GENERATED_JAR_FILE)


def clean_flink_output_files():
    output_files = [BaseConfig.Q3_OUTPUT_DATA_FILE,
                    BaseConfig.Q6_OUTPUT_DATA_FILE,
                    BaseConfig.Q10_OUTPUT_DATA_FILE,
                    BaseConfig.Q18_OUTPUT_DATA_FILE]

    for strfile in output_files:
        if os.path.exists(strfile):
            os.truncate(strfile, 0)
            logging.info('truncate the output data file : ' + strfile)
        else:
            f = open(strfile, 'w')
            f.close()


def r_run_flink_task(filename, queue):
    from config import BaseConfig

    if filename == '':
        ret = subprocess.CompletedProcess(args='', returncode=1, stdout="filename is null.")
        return ret

    generated_jar_file_path = os.path.join(BaseConfig.GENERATED_JAR_PATH, filename)
    if not os.path.exists(generated_jar_file_path):
        ret = subprocess.CompletedProcess(args='', returncode=1, stdout="generated jar does not exist.")
        return ret

    generated_jar_para = ""
    flink_command_path = os.path.join(BaseConfig.FLINK_HOME_PATH, "bin/flink")
    if BaseConfig.REMOTE_FLINK:
        cmd_str = flink_command_path + " run " + " -m " + BaseConfig.REMOTE_FLINK_URL + " " + generated_jar_file_path \
                  + " " + generated_jar_para
    else:
        cmd_str = flink_command_path + " run " + generated_jar_file_path + " " + generated_jar_para

    logging.info("flink command: " + cmd_str)

    clean_flink_output_files()

    ret = subprocess.run(cmd_str, shell=True, capture_output=True)
    result = str(ret.stdout) + str('\n') + str(ret.stderr)
    logging.info('flink jobs return: ' + result)

    aju_app.r_send_query_result_data_from_socket(queue)
    return ret
