# Trajectory Optimization Library

## 1 Introduction

Trajectory optimization is a software library for robotic motion planning. The core libraries are implemented in C++. The library has been tested on Ubuntu 16.04.

## 2 Setup

### 2.1 Third-Party dependencies

1) [IPOPT](https://projects.coin-or.org/Ipopt)
2) [CMake](https://cmake.org/)
3) [GNUPlot](http://www.gnuplot.info/) (Optional, used for trajectory visualization)
4) [MuJoCo](http://www.mujoco.org)
5) [GTest](https://github.com/google/googletest)


### 2.2 Installation instructions

#### 2.2.1 IPOPT Installation

1) Download the source code from https://www.coin-or.org/download/source/Ipopt/ , and then upack IPOPT in the home directory.
```
wget http://www.coin-or.org/download/source/Ipopt/Ipopt-3.12.4.tgz
tar xvzf Ipopt-3.12.4.tgz
```

2) Get IPOPT third-party packages:
```
cd ~/Ipopt-3.12.4/ThirdParty/Blas
./get.Blas
cd ../Lapack
./get.Lapack
cd ../Mumps
./get.Mumps
cd ../Metis
./get.Metis
cd ../../
```
3) Compile IPOPT:
```
cd ~/Ipopt-3.12.4/
mkdir build
cd build
../configure
make -j 4` #Compile using 4 cores (if you have them) 
make install
```

#### 2.2.2 CMake Installation



#### 2.2.3 GNUPlot Installation
`sudo apt-get install gnuplot`

#### 2.2.4 MuJoCo Installation

#### 2.2.5 GTest Installation

#### 2.2.6 `setup.sh` script for Mac-based system
(A script `setup.sh` has been provided to install the first three dependencies on a Mac-based system. It will install Homebrew and use it to install the first three dependencies. To execute it, run `chmod +x setup.sh && ./setup.sh`.)

Linux support has not been added to the script yet.



### 2.3 Common Installation Issues

If you have encountered one of the following issues, please try the suggestion below.

#### 2.3.1 IPOPT related issues

1) Could not find Blas
```
sudo apt-get install gfortran
```
2) You may need to update your gcc-5 to gcc-7 instructed by the following link https://gist.github.com/jlblancoc/99521194aba975286c80f93e47966dc5 . After that, When you make executable, you may run into “could not find -lgfortran”. You can solve this issue by copying filename formed as "\*libgfortran" in gcc 5 (4 files probably in gcc 5) into 7.3.0 (or your current gcc version).


#### 2.2.1 IPOPT Installation



### How to use TrajectoryOptimization

TrajectoryOptimization can be easily used as a git submodule in any other CMake-based project. Let's walk through integrating TrajectoryOptimization into an existing source project.

1) cd into your project directory, `git init` if it isn't already a git repository.
2) `mkdir -p lib && git submodule add [insert this project's clone URL (https/ssh)] lib/trajectoryOptimization`
3) If you don't already use CMake, run `touch CMakeLists.txt`. Insert `cmake_minimum_required(VERSION 3.8)` as the first line.
5) Insert these into your `CMakeLists.txt` to import and link the `TrajectoryOptimization::TrajectoryOptimizationLib` target:
```
add_subdirectory(lib/trajectoryOptimization)
add_executable([yourExecutableName] [yourSourceFiles])
target_link_libraries([yourExecutableName]
  PUBLIC
    TrajectoryOptimization::TrajectoryOptimizationLib
)
```
6) `mkdir build && cd build && cmake ..`
7) `make`
8) `./[yourExecutableName]`

Now you can build software using TrajectoryOptimization!

To ever recompile and rerun, just cd into `build/` and run `make && ./[yourExecutableName]`.

### Running tests

To build tests, run cmake like this: `cmake -Dtraj_opt_build_tests=ON ..`. Then cd into `lib/trajectoryOptimization` and run `ctest`.

### Running samples

To build samples, run cmake like this: `cmake -Dtraj_opt_build_samples=ON ..`. Then cd into `lib/trajectoryOptimization` and run `./trajectoryOptimizationSample`. The sample currently optimizes a 3D trajectory. Inspect [the source](src/trajectoryOptimizationMain.cpp) for more information and to learn about usage.

### Notes about Mujoco

Mujoco support is currently baked into this project, but disabled.

To enable building/linking it:
1) Uncomment the relevant lines in [CMakeLists.txt](CMakeLists.txt) that are marked for Mujoco.
2) Copy [this file](cmake/LocalProperties.cmake.sample) to cmake/LocalProperties.cmake and replace the FIXME with the path to your Mujoco installation.
