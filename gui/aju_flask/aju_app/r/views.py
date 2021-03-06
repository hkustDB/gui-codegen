import aju_app
from . import r
from .. import aju_utils
import config
from flask import render_template, request, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename

import os
import shutil
import logging
import time
import threading
from multiprocessing import Process, Queue
from aju_app import socketio


@socketio.on('r_connect', namespace='/ws')
def r_socket_connect(data):
    print("r_socket_connect: ", data)
    socketio.emit('r_socket_connect', {'data': 1})


@r.route('/r')
def index():
    return "here are flask r."
    # aju_utils.clean_codegen_log_and_generated_jar();
    # return render_template('index.html')


@r.route('/r/upload', methods=['POST'])
def upload_json_file():

    # start socket server background process
    from multiprocessing import Process
    p = Process(target=aju_app.r_run_socket_server, args=(aju_app.queue,))
    p.start()

    aju_app.r_set_step_to(0)
    aju_app.stop_send_data_thread()

    f = request.files['json_file']
    uploaded_json_filename = secure_filename(f.filename)
    query_idx = aju_utils.get_query_idx(uploaded_json_filename)
    uploaded_json_file_save_path = os.path.join(config.JSON_FILE_UPLOAD_PATH, uploaded_json_filename)

    # check if the upload dir exists or not
    if not os.path.exists(config.JSON_FILE_UPLOAD_PATH):
        os.makedirs(config.JSON_FILE_UPLOAD_PATH)

    # save the json file to server
    f.save(uploaded_json_file_save_path)

    # check if the uploaded file is json file
    if not aju_utils.is_json_file(uploaded_json_file_save_path):
        # remove the uploaded non json file
        if os.path.exists(uploaded_json_file_save_path):
            os.remove(uploaded_json_file_save_path)

    # remove the older generated-code directory
    if os.path.isdir(config.GENERATED_CODE_DIR):
        shutil.rmtree(config.GENERATED_CODE_DIR)
        logging.info('remove the generated-code directory.')

    aju_app.r_set_step_to(1)
    # call the codegen to generate a jar file
    codegen_log_result, retcode = aju_utils.run_codegen_to_generate_jar(uploaded_json_file_save_path, query_idx)

    aju_app.r_send_codgen_log_and_retcode(codegen_log_result, retcode)
    print('retcode: ', retcode)
    if retcode != 0:
        aju_app.r_send_message("error", "codegen failed!")
        # aju_app.r_set_step_to(1)
        return "codegen failed."

    print("query id: ", str(query_idx))
    aju_utils.r_run_flink_task(config.GENERATED_JAR_FILE, query_idx, aju_app.queue)

    return codegen_log_result


@r.route("/r/download_codegen_log")
def r_download_codegen_log():
    print("r_download_codegen_log")
    if os.path.exists(config.CODEGEN_LOG_FILE):
        return send_from_directory(config.CODEGEN_LOG_PATH, 'codegen.log', as_attachment=True)
    else:
        pass


@r.route("/r/download_generated_jar")
def r_download_generated_jar():
    print("r_download_generated_jar")
    if os.path.exists(config.GENERATED_JAR_FILE):
        return send_from_directory(config.GENERATED_JAR_PATH, 'generated.jar', as_attachment=True)
    else:
        pass
