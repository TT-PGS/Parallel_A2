CXX        := g++
CXXFLAGS   := -std=c++11 -O2
LDFLAGS_MT := -pthread

# MPI include + library paths on Windows (Microsoft MPI)
MPI_INCL := -I"C:\Program Files (x86)\Microsoft SDKs\MPI\Include"
MPI_LIBS := -L"C:\Program Files (x86)\Microsoft SDKs\MPI\Lib\x64" -lmsmpi

TARGETS := astar_sequential astar_multithread astar_openmp

.PHONY: all clean

all: $(TARGETS)

astar_sequential: astar_sequential.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

astar_multithread: astar_multithread.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS_MT) -o $@ $<

astar_openmp: astar_openmp.cpp
	$(CXX) $(CXXFLAGS) $(MPI_INCL) $< -o $@ $(MPI_LIBS) 


clean:
	rm -f $(TARGETS)
