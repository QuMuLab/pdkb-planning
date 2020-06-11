
# Converting from PDKBDDL to EPDDL

First thing to note: ***THIS IS NOT RECOMMENDED***.

Why? Well a direct conversion, at least as it's implemented here, side-steps all of the power and beauty of the fully flexible doxastic reasoning that MEPK variants are capable of handling in the broad EPDDL language.

But it you must (e.g., to capture all of the cascade in PDKBDDL processing), then here are the steps.

## Instructions

1. In the `pdkb/actions.py` file, find the `pddl` method of the `CondEff` class.

2. Change the `EPDDL` flag from `False` to `True` and re-install the package.

3. Run the planner and keep the files around (note that this will fail to find a plan): `python3 -m pdkb.planner <problem> --keep-files`

4. Modify the `convert.py` file ("Custom swaps") to replace the belief/possibility notation.

5. Run the conversion: `python3 convert.py pdkb-domain.pddl pdkb-problem.pddl output.epddl`

6. Manually edit the `:predicates` section at the top of `output.epddl` to only contain primitve fluents (no nesting or negations)

This is a brittle process. The above steps have been tested with the `example.pdkbddl` file included in this directory, and `output.epddl` is the result. When running MEPK, generally the errors are quite clear and indicitive of what's going wrong with the conversion.

Feel free to [reach out](mailto:christian.muise@queensu.ca) if you have any questions.
