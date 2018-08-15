# Example Dockerfile for setting up Docker container with MiniConda and an
# example app.

FROM ubuntu:16.04

# System packages 
RUN apt-get update && apt-get install -y curl && apt-get install -y bzip2 bzip2-libs

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
RUN bash Miniconda-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

# Python packages from conda
RUN conda install -y \
    scikit-image \
    flask \
    pillow

# Setup application
