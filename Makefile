# Makefile for building A* C++ versions

CXX = g++
CXXFLAGS = -O2 -std=c++17

all: astar_sequential_cpp astar_multithread_cpp astar_openmp_cpp

astar_sequential_cpp: astar_sequential.cpp
	$(CXX) $(CXXFLAGS) astar_sequential.cpp -o astar_sequential_cpp

astar_multithread_cpp: astar_multithread.cpp
	$(CXX) $(CXXFLAGS) astar_multithread.cpp -o astar_multithread_cpp

astar_openmp_cpp: astar_openmp.cpp
	$(CXX) $(CXXFLAGS) -fopenmp astar_openmp.cpp -o astar_openmp_cpp

clean:
	rm -f astar_sequential_cpp astar_multithread_cpp astar_openmp_cpp
