FROM zhiyuli/rapid_base:1.0

RUN apt-get update && apt-get install -y \
    libssl-dev \
    libffi-dev \
    python2.7 \
    python-pip \
    axel

RUN cd ~ && \
    git clone https://github.com/BYU-Hydroinformatics/RAPIDpy.git && \
    git clone https://github.com/BYU-Hydroinformatics/spt_compute.git && \
    git clone https://github.com/erdc-cm/spt_dataset_manager.git
 
RUN pip install Rtree==0.8.3 \
    requests_toolbelt \
    condorpy \
    boto3 \
    Cython \
    tethys_dataset_services \
    future \
    azure-storage-file


RUN cd ~/RAPIDpy && \
    python setup.py install && \
    cd ../ && \
    cd spt_dataset_manager && \
    python setup.py install && \
    cd ../ && \
    cd spt_compute && \
    python setup.py install

RUN cd /home && \
    mkdir mp_execute \
    era_interim \
    subprocess_logs \
    logs \
    ecmwf_data

ADD scripts/init.sh /opt/init.sh
ADD run_script.py /home/run_script.py

CMD ["/bin/bash", "/opt/init.sh"]