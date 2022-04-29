FROM nvidia/cuda:11.6.2-cudnn8-devel-ubuntu20.04 as base

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get -y install ssh
RUN apt-get -y install python3-pip
RUN apt-get -y install htop
RUN apt-get -y install libpq-dev

RUN apt-get update 
RUN apt-get -y install cmake libopenmpi-dev python3-dev zlib1g-dev libgl1-mesa-dev

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools

RUN useradd -ms /bin/bash selfplay
USER selfplay
ENV PATH="/home/selfplay/.local/bin:${PATH}"
WORKDIR /app
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
COPY --chown=selfplay:selfplay ./app/requirements.txt /app
RUN pip3 install -r /app/requirements.txt
RUN pip3 install stable_baselines3
RUN pip3 install mpi4py
COPY --chown=selfplay:selfplay ./app .

ENV PYTHONIOENCODING=utf-8
ENV LC_ALL=C.UTF-8
ENV export LANG=C.UTF-8

CMD bash
