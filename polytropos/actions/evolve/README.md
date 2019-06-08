# Metamorphoses, changes, and lookups

Some variables are specific to a particular entity, but do not come directly from an external source. These variables
are *derived* through some change process. These change processes are defined as Python files *within* the
configuration. 

The module that contains the Changes is added to the classpath dynamically at runtime. Each Change class must have a 
name that is globally unique within the project. At runtime, all of the .py files in the `changes` directory are scanned
for subclasses of Change. The name of the class is used to identify it in a metamorphosis definition.

The Changes are instantiated after the variable schemas have been loaded, such that the particular variables to be 
altered can be identified by ID, validated, and converted into a Variable object to be used within the process.

A sequence of Changes is called a Evolve. Because the Evolve applies to only one entity (i.e., one 
composite), the sequence can be applied to many Composites in parallel.

Some Changes depend on simple external Lookups. These must be specified explicitly in the Evolve
definition. At construction time, the Evolve will verify that its required Lookups have been loaded. 

The assumption with Lookups is that they have a simple foreign-key relationship to the data and that they are small 
enough to fit in memory. (External data not meeting these requirements will need to be merged in through some other 
process, inevitably less amenable to parallelism and concurrency.)
