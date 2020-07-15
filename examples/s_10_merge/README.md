* `p` is missing `composite_1.json`.
* `q` is missing `composite_2.json`.
* In `composite_4.json`:
  * `p` is missing `period_2`
  * `q` is missing `period_1`
  * `p` is missing `/immutable/simple_keyed_list/nl_1`.
  * `q` is missing `/immutable/simple_keyed_list/nl_2/some_text`
* In `composite_3.json`:
  * `p` is missing `/period_1/t_folder`.
  * `q` is missing `/period_2/t_folder/some_text`.
  * `q`:
    * is missing all but the first entry of `/period_2/t_list`
    * has a corrupted value for the first element of `/period_1/t_list/some_text`
    * has a corrupted value of `/period_1/t_folder/some_text`
    * has a field that doesn't exist in the schema (but that should show up anyway)