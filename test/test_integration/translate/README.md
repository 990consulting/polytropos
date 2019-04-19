# Translation lifecycle tests

The translation lifecycle tests verify that the translation machinery works. The tests integrate Variable, Track, and 
Translate, but do not depend on any other systems.

The test suite files are numbered in order of complexity. If a lower-numbered one does not pass, it is very likely that 
all the higher-numbered tests will fail as well.