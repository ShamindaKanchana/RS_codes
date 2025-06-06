SCHIFRA_DIR = /home/shaminda/Documents/My Projects/RS_codes/schifra
INCLUDES = -I$(SCHIFRA_DIR) -I./include
CXXFLAGS = -std=c++17 $(INCLUDES)

SOURCES = $(wildcard src/*.cpp)
OBJECTS = $(SOURCES:.cpp=.o)

all: dna_rs_example

dna_rs_example: $(OBJECTS)
	$(CXX) $(OBJECTS) -o $@ $(CXXFLAGS)

clean:
	rm -f $(OBJECTS) dna_rs_example
