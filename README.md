# pydozor_libs

## Description
python interface to Dozor, https://git.embl.de/bourenko/dozor

## Requirements
- numpy
- python
- cffi
- bitshuffle
- h5py

## Instatll
1. Download Dozor source code
2. change the Makefile 

## Usage
- dozor.py is the python interface to call dozor(Fortran) shared library
  dozor.dat(slightly shortened version comparing to the original one) is required to initilize the object, see dozor_example.dat
- dozor_offline.py, analyze the Eiger hdf5 data using dozor.py, a demonstration of how to use the dozor.py. To run it,
  python dozor_offline.py -m xxxx_master.h5
  use -h for more options

## Instruction to compile dozor shared library
1. Modify the makefile of dozor, by adding "-fPIC" in the FCFLAGS
2. Compile dozor
3. compile the shared library by running the following command
   `gfortran -fopenmp -o libdozor.so -shared -fPIC dozor_submain.o dozor_auxiliary_lib.o anis_gleb_all.o hkl_direct.o scancl.o`
4. add libdozor.so into the LD_LIBRARY_PATH as below
   `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/your/libdozor/path/`
