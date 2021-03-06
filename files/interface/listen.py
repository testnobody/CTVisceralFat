from common.utils import *
from common import listener_server
import time
import os
import subprocess as sb
from common import utils
import shutil
import os

# PRE: for nifti files source_files=/path/to/volume.nii.gz
def visceral_fat_measure_nifti(param_dict):

    print("### ct visceral fat got parameters {}".format(param_dict))
    data_share = os.environ["DATA_SHARE_PATH"]

    rel_source_file = param_dict["source_file"][0]

    # remove trailing / at the beggining of name
    # otherwise os.path.join has unwanted behaviour for base dirs
    # i.e. join(/app/data_share, /app/wrongpath) = /app/wrongpath
    rel_source_file = rel_source_file.lstrip('/')

    source_file = os.path.join(data_share, rel_source_file)

    log_debug("### source file", source_file)
    report_path, success = visceral_fat_measure_nifti_single(source_file)


    result_dict = {"fat_report": report_path}

    return result_dict, success

def __create_tmp_out_dir():

    unique_id = utils.get_unique_id()
    tmp_dir = os.path.join("/tmp", f"output-{unique_id}")

    if os.path.exists(tmp_dir):
        log_debug(f"tmp output directory exists, removing - {tmp_dir}")
        shutil.rmtree(tmp_dir)

    os.makedirs(tmp_dir)

    return tmp_dir

def visceral_fat_measure_nifti_single(source_file):

    tmp_output_dir = __create_tmp_out_dir()

    visc_fat_command = f"cd {tmp_output_dir} && /app/NIH_FatMeasurement --nogui -d {source_file}"

    data_share = os.environ["DATA_SHARE_PATH"]

    log_debug("Calling", visc_fat_command)
    exit_code_fat_measure = sb.call([visc_fat_command], shell=True)

    if exit_code_fat_measure == 1:
        return None, False

    volume_name = os.path.split(source_file)[1]
    source_file_name = volume_name[:len(volume_name) - 7]  # remove .nii.gz

    report_name = "FatReport_" + volume_name + ".txt"
    report_fn = os.path.join(tmp_output_dir, report_name)

    unique_id = utils.get_unique_id()
    new_report_name = "ct_fat_FatReport_" + source_file_name + "_" + unique_id + ".txt"
    new_report_path = os.path.join(data_share, new_report_name)
    mv_command = "mv {} {}".format(report_fn, new_report_path)
    exit_code_mv = sb.call([mv_command], shell=True)

    shutil.rmtree(tmp_output_dir)

    if exit_code_mv == 1:
        return None, False

    return new_report_name, True

# PRE: for dcm files   source_file=/path/to/dir
def visceral_fat_measure_dcm(param_dict):

    # ### DEPRECATED

    assert False
    # because of a bug in generating the report in CTVisceralFat
    # need to run NIH_FatMeasurement, the -d argument
    # needs to be just the directory name, not a path with slashes
    # i.e.  NIH_FatMeasurement -d /path/to/dcm/dir     ERRORS OUT
    # wants NIH_FatMeasurement -d dir

    print("### ct visceral fat got parameters {}".format(param_dict))
    data_share = os.environ["DATA_SHARE_PATH"]

    rel_source_file = param_dict["source_file"][0]
    source_file = os.path.join(data_share, rel_source_file)

    cp_cmd = "cp -r {} /tmp/".format(source_file)
    print("running {}".format(cp_cmd))
    exit_code_cp = sb.call([cp_cmd], shell=True)

    if exit_code_cp == 1:
        return {}, False


    dir_name = os.path.split(rel_source_file)[1]

    visc_fat_command = "cd /tmp && /app/NIH_FatMeasurement --nogui -d {}".format(dir_name)

    print("running {}".format(visc_fat_command))
    exit_code_fat_measure = sb.call([visc_fat_command], shell=True)

    if exit_code_fat_measure == 1:
        return {}, False

    report_name = "FatReport_" + dir_name + ".txt"
    report_fn   = os.path.join("/tmp", report_name)

    print(report_fn)

    new_report_name = "ct_fat_FatReport_" + dir_name + "_" + str(time.time()) + ".txt"
    new_report_path = os.path.join(data_share, new_report_name)
    mv_command = "mv {} {}".format(report_fn, new_report_path)

    print("running {}".format(mv_command))

    exit_code_mv = sb.call([mv_command], shell=True)

    if exit_code_mv == 1:
        return {}, False

    result_dict = {"fat_report": new_report_path}

    return result_dict, True


if __name__ == '__main__':

    setup_logging()
    log_info("Started listening")

    served_requests = {
        "/ct_visceral_fat_dcm": visceral_fat_measure_dcm,
        "/ct_visceral_fat_nifti": visceral_fat_measure_nifti
    }

    listener_server.start_listening(served_requests, multithreaded=True, mark_as_ready_callback=mark_yourself_ready)

