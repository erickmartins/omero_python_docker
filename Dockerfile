# Example Dockerfile for setting up Docker container with MiniConda and an
# example app.

FROM ubuntu:16.04

# System packages 
RUN apt-get update && apt-get install -y curl && apt-get install -y bzip2 

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
RUN bash Miniconda-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

# Set up bioconda channel

RUN conda config --add channels defaults
RUN conda config --add channels conda-forge
RUN conda config --add channels bioconda


# Python packages from conda
RUN conda install -y \
    python-omero \
    numpy

# Setup application
ADD ./CreateImageAdvanced.py /python-code/
ADD ./Parse_OMERO_Properties.py /python-code/
ADD ./Connect_to_OMERO.py /python-code/
ADD ./concat_files_janelia.py /python-code/
ADD ./save_ome_tiff.py /python-code/