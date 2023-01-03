TensorOcean
========

TensorOcean is a part of MPAS-Ocean (LA-CC-13-047) and implements some routines of MPAS-Ocean in PyTorch for research purposes. The project goal is to help accelerate MPAS-Ocean by using AI accelerators (e.g., Google's TPU) through efficient transformations from discretized operators in ocean modeling to regular tensor operations in PyTorch.

Implementations
-----------

We have implemented four sub-tasks of MPAS-Ocean's tracer advection routine in PyTorch: (1) computing high-order vertical fluxes, (2) accumulating scaled high-order vertical tendencies, (3) computing high-order horizontal fluxes, and (4) accumulating scaled high-order horizontal tendencies. For (1) and (2), we have one baseline PyTorch implementation retaining the original MPAS-Ocean indexing system. For (3) and (4), we have two PyTorch implementations (i.e., baseline and optimized) that base on different indexing systems. Baseline_xpu.py includes (1)-(4), and optimized_xpu.py includes (3)-(4).

To run on different processors, the PyTorch implementations only need to change a few lines of code. We have tested our PyTorch implementations on CPU, GPU, and TPU. Please see the code in the PyTorch folder. We also include the original Fortran implementation with both OpenMP and OpenACC for comparison purposes.

Usage
------------

The meshgen.c file can generate configurable hexagonal meshes with the format of LENGTHxDEPTHxTRACERS. A single-generated mesh can be used as the input of the original Fortran implementation and the baseline PyTorch implementation. The optimized PyTorch implementation currently uses dimension sizes as the input.

Example of running on CPU:
gcc -o meshgen.exe -O2 meshgen.c
meshgen.exe 100 100 1
python3 baseline_cpu.py 100x100x100_1.dat

Publications
--------------------------

Li Tang, Philip Jones and Scott Pakin, "Harnessing Extreme Heterogeneity for Ocean Modeling with Tensors," The 2nd International Workshop on Extreme Heterogeneity Solutions (ExHET 2022), (Under review).

Legal statement
---------------

Copyright (c) 2013-2019, Los Alamos National Security, LLC (LANS) (Ocean: LA-CC-13-047; Land Ice: LA-CC-13-117) and the University Corporation for Atmospheric Research (UCAR).
All rights reserved.

LANS is the operator of the Los Alamos National Laboratory under Contract No. DE-AC52-06NA25396 with the U.S. Department of Energy. UCAR manages the National Center for Atmospheric Research under Cooperative Agreement ATM-0753581 with the National Science Foundation. The U.S. Government has rights to use, reproduce, and distribute this software. NO WARRANTY, EXPRESS OR IMPLIED IS OFFERED BY LANS, UCAR OR THE GOVERNMENT AND NONE OF THEM ASSUME ANY LIABILITY FOR THE USE OF THIS SOFTWARE. If software is modified to produce derivative works, such modified software should be clearly marked, so as not to confuse it with the version available from LANS and UCAR.

More details can be found at https://github.com/lanl/TensorOcean/blob/main/LICENSE

Contact
-------

Li Tang, *ltang@lanl.gov*
