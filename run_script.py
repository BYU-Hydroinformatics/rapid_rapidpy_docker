# -*- coding: utf-8 -*-
from spt_compute import run_ecmwf_forecast_process
# ------------------------------------------------------------------------------
# main process
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    run_ecmwf_forecast_process(
        rapid_executable_location='/root/rapid/src/rapid',
        rapid_io_files_location='/home/rapid-io',
        ecmwf_forecast_location="/home/ecmwf_data",
        era_interim_data_location="/home/era_interim",
        subprocess_log_directory='/home/subprocess_logs',
        main_log_directory='/home/logs',
        data_store_url='',
        data_store_api_key='',
        data_store_owner_org='',
        app_instance_id='',
        sync_rapid_input_with_ckan=False,
        download_ecmwf=True,
        ftp_host="data-portal.ecmwf.int",
        ftp_login="safer",
        ftp_passwd="neo2008",
        ftp_directory="tcyc",
        date_string="*.00",
        region="",
        upload_output_to_ckan=False,
        initialize_flows=True,
        create_warning_points=True,
        warning_flow_threshold=30,
        delete_output_when_done=False,
        mp_mode='multiprocess',
        mp_execute_directory='/home/mp_execute',
        accelerate_download=True,
        num_connections=15
    )
