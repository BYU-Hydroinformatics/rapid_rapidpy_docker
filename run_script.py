from datetime import datetime
from RAPIDpy.inflow import run_lsm_rapid_process
# ------------------------------------------------------------------------------
# main process
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    run_lsm_rapid_process(
        rapid_executable_location='/root/rapid/run/rapid',
        rapid_io_files_location='/home/rapid-io',
        lsm_data_location='/home/ERA-5_hourly_data',  # path to folder with LSM data
        simulation_start_datetime=datetime(1979, 1, 1),
        simulation_end_datetime=datetime(2018, 12, 31),
        generate_rapid_namelist_file=True,  # if you want to run RAPID manually later
        run_rapid_simulation=True,  # if you want to run RAPID after generating inflow file
        generate_return_periods_file=True,  # if you want to get return period file from RAPID simulation
        return_period_method='weibull',
        generate_seasonal_averages_file=True,
        generate_seasonal_initialization_file=True,  # if you want to get seasonal init file from RAPID simulation
        generate_initialization_file=False,  # if you want to generate qinit file from end of RAPID simulation
        use_all_processors=True
    )
