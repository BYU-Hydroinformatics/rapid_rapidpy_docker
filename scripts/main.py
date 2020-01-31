import multiprocessing
import datetime
import os
import time
from glob import glob
import pandas as pd
import xarray
import psycopg2
import psycopg2.extras
import copy
import logging

# This will need to come from a database query


OUTPUT_DIR = "/Users/rohitfun/git/test_output"
ENSEMBLE_TABLE = "ensemblenepal2"
FORECAST_TABLE = "forecastnepal2"
COMIDS_TABLE = "nepaldnetwork"
conn = psycopg2.connect(host="192.168.10.6", database="servirFlood", user="rohit", password="R04it##.")


def get_last_run_date():
    try:
        with conn.cursor() as cursor:
            postgreSQL_select_Query = "SELECT MAX (rundate) from " + ENSEMBLE_TABLE

            cursor.execute(postgreSQL_select_Query)
            run_date = cursor.fetchall()

            if run_date[0][0] is not None:
                return run_date[0][0]
            else:
                return datetime.datetime(1990, 1, 1)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def get_comids(tableName):
    try:
        with conn.cursor() as cursor:
            postgreSQL_select_Query = "select comid from " + tableName

            cursor.execute(postgreSQL_select_Query)
            com_ids = cursor.fetchall()

            return_ids = []
            for com_id in com_ids:
                return_ids.append(com_id[0])
        return return_ids

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def make_filter(date):
    def date_filter(folderName):
        folder_date = datetime.datetime.strptime(folderName.split(".")[0], "%Y%m%d")
        return folder_date > date
    return date_filter


def find_ecmwf_files(output_directory, prev_run_date):

    if not os.path.exists(output_directory):
        return None, None

    dates = \
        sorted(
            [d for d in os.listdir(output_directory)
             if os.path.isdir(os.path.join(output_directory, d))],
            reverse=True
        )

    filter_date = make_filter(prev_run_date)
    filtered_dates = list(filter(filter_date, dates))

    return filtered_dates


def insert_execute_batch(connection, all_timesteps, table_name) -> None:
    try:
        with connection.cursor() as cursor:
            cols = all_timesteps['cols']
            cols_str = ','.join(cols)
            vals_str = ','.join(['%s' for i in range(len(cols))])
            sql_str = """INSERT INTO {} ({}) VALUES ({})""".format(table_name, cols_str, vals_str)
            psycopg2.extras.execute_batch(cursor, sql_str, all_timesteps['values'])
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def do_insert(rec: dict, cur, table_name):
    try:
        cols = rec.keys()
        cols_str = ','.join(cols)
        vals = [rec[k] for k in cols]
        vals_str = ','.join(['%s' for i in range(len(vals))])
        sql_str = """INSERT INTO {} ({}) VALUES ({})""".format(table_name, cols_str, vals_str)
        cur.execute(sql_str, vals)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def process_rivid(riv_id, ensemble_data_cols, forecast_data_cols, merged_ds, run_date, conn):
    # start = time.time()

    riv_ensemble = {"cols": ensemble_data_cols, "values": []}
    riv_forecast = {"cols": forecast_data_cols, "values": []}

    selected_dataset = merged_ds.sel(rivid=riv_id)

    merged_ds_mean = selected_dataset.mean(dim='ensemble').to_dataframe().Qout
    merged_max = selected_dataset.min(dim='ensemble').to_dataframe().Qout
    merged_min = selected_dataset.max(dim='ensemble').to_dataframe().Qout
    merged_std_ar = selected_dataset.std(dim='ensemble').to_dataframe().Qout

    qout_ensemble_dfs = {}
    for i in range(1, 53):
        qout_ensemble_dfs[i] = selected_dataset.sel(ensemble=i).to_dataframe().Qout

    high_res_df = qout_ensemble_dfs[52]

    for each_time_step in selected_dataset.time.values:
        ensemble_ts = []

        for i in range(1, 53):
            try:
                ensemble_ts.append(float(qout_ensemble_dfs[i][each_time_step]))
            except (Exception) as error:
                print(error)
                ensemble_ts.append(None)
                pass

        time_step_dt = datetime.datetime.utcfromtimestamp(each_time_step.tolist()/1e9)
        ensemble_ts.append(time_step_dt.strftime("%Y-%m-%d %H:%M:%S"))
        ensemble_ts.append(run_date)
        ensemble_ts.append(int(riv_id))
        # Create row and push data
        riv_ensemble['values'].append(ensemble_ts)

        forecast_row = []
        try:
            forecast_row.append(float(high_res_df[each_time_step]))
        except (Exception) as error:
            # print(error)
            forecast_row.append(None)
            pass

        try:
            forecast_row.append(float(merged_ds_mean[each_time_step]))
            forecast_row.append(float(merged_min[each_time_step]))
            forecast_row.append(float(merged_max[each_time_step]))
            forecast_row.append(float(
                merged_ds_mean[each_time_step] + merged_std_ar[each_time_step]))
            forecast_row.append(float(
                merged_ds_mean[each_time_step] - merged_std_ar[each_time_step]))
            time_step_dt = datetime.datetime.utcfromtimestamp(each_time_step.tolist()/1e9)
            forecast_row.append(time_step_dt.strftime("%Y-%m-%d %H:%M:%S"))
            forecast_row.append(run_date)
            forecast_row.append(int(riv_id))
            forecast_row.append(0)
        except (Exception) as error:
            # print(error)
            pass
        riv_forecast['values'].append(forecast_row)

    insert_execute_batch(conn, riv_ensemble, ENSEMBLE_TABLE)
    insert_execute_batch(conn, riv_forecast, FORECAST_TABLE)
    # logging.info("DB Insert Completed. Comid:" + str(riv_id) + " done.")
    conn.commit()
    # end = time.time()
    # logging.info('total time for subprocess (s)= ' + str(end-start))


# MAIN CODE
logging.basicConfig(level=logging.INFO)
start = time.time()
last_run_date = get_last_run_date()

# Can be used later if we have proper comids in the DB
# comids = get_comids(COMIDS_TABLE)

dates = find_ecmwf_files(OUTPUT_DIR, last_run_date)

for date in dates[0:1]:
    logging.info("Processing Output from date: " + date)
    date_dir = os.path.join(OUTPUT_DIR, date)
    basin_files = sorted(glob(os.path.join(date_dir, "*.nc")), reverse=True)
    run_date = datetime.datetime.strptime(date.split(".")[0], "%Y%m%d")
    riv_comids = xarray.open_dataset(basin_files[0]).rivid.sel().values

    ensemble_data_cols = []
    forecast_data_cols = []

    for i in range(1, 53):
        ensemble_data_cols.append('ensemble'+str(i))

    ensemble_data_cols.append('forecastdate')
    ensemble_data_cols.append('rundate')
    ensemble_data_cols.append('comid')

    forecast_data_cols = [
        'high_res',
        'meanval',
        'minval',
        'maxval',
        'std_dev_range_upper',
        'std_dev_range_lower',
        'forecastdate',
        'rundate',
        'comid',
        'riskfactor'
    ]

    qout_datasets = []
    ensemble_index_list = []

    logging.info("merging ensembles into memory")

    for forecast_nc in basin_files:
        ensemble_index_list.append(
            int(os.path.basename(forecast_nc)[:-3].split("_")[-1])
        )
        qout_datasets.append(
            xarray.open_dataset(forecast_nc).Qout
        )

    merged_ds = xarray.concat(qout_datasets, pd.Index(ensemble_index_list, name='ensemble'))
    logging.info("merging ensembles into memory completed")

    for dataset in qout_datasets:
        dataset.close()
    k = 1
    for riv_id in riv_comids:
        logging.info("Processing Comid: " + str(riv_id) + ". " + str(k) + " of " + str(len(riv_comids)))
        k = k+1
        process_rivid(riv_id, ensemble_data_cols, forecast_data_cols, merged_ds, run_date, conn)


end = time.time()
logging.info('total time (s)= ' + str(end-start))
