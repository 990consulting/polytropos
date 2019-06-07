# Lookup tables

It is very common to have data to which one wishes to append particular values based on a lookup table. Lookup tables
are intended to be small enough to fit into memory, and should have a one-to-one correspondence with some foreign key in
a schema. Because of these properties, lookup tables can be used within a Metamorphosis, where they are available as
reference material for every Change.
