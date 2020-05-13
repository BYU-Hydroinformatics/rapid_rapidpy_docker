# Dockerized RapidPY to run HIWAT

### Run Instructions

-   Clone this github Repo and switch to the branch `nepal_hiwat`
-   Run `docker-compose build --no-cache` to build the docker image
-   Run `docker-compose up -d` to start the container
-   Place the input files (the regional files with weight tables) in the `input_data` directory that should have been created
-   Place the Input HIWAT files in the `input_dataset` directory
-   Run `docker exec -it hiwat_rapid bash` to get access to the container
-   Run the command `python /home/run_script.py` within the container to start the processing
-   Once the process is done running, you can check the `output_files` directory for the output files.
-   Type `exit` at any time to leave the container
