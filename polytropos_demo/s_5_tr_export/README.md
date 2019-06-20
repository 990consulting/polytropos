# Export scenarios

These scenarios introduces several things:

1. We are introducing `Translate` as a task step.

2. We are introducing the `Consume` step, which (as its name implies) consumes all of the composites, terminating a
`task` pipeline without a `results_in` output. Notably, the output of the `Consume` step is controlled by the logic of
the step itself, and consequently can end anywhere--in some arbitrary file, in a database, printed to the screen, 
whatever.

3. We are introducing the idea that we need to look for step definitions both in the user-supplied `conf` directory and
inside the `polytroposa` codebase itself. In this case, we have scenarios for two built-in `Consume` steps (`to_csv` and 
`to_json`) as well as one custom `Consume` step, `count` (which trivially prints the number of composites to `stdout`).

4. The `to_csv` step requires handling nested lists via a cartesian product, and supplies column names and orders right
inside the `task.yaml` file, which is a little different from how we've used this file so far.

5. The `to_json` step requires a little bit of custom code to implement a streaming JSON dictionary writer. This is
possible for the particular case of the composites because we know that every composite has a unique ID (to be used as
the key) and consists of valid JSON (to be used as the value).
