BUGS
* if data has no injuries or all injuries and is processed with 
  `external.sep=TRUE`, if fails with a cryptic indexing error
* if you pass a burnin greater than the Nsim you get a cryptic java error
* if you redefine the conditional probability and no causes+symptoms pairs are
  impossible and you do not pass `exclude.impossible.cause=FALSE`, it fails
  with a cryptic data is null error. This happens when you go to cast 
  `impossible <- as.matrix(impossible)` (InSilicoVA/R/insilico_core.r line 628)
* Doesn't fully validate 'type' when calling `extract.prob`. This leads to an
  indexing error later.

API
* `nlevels.dev` has a hidden default at InSilicoVA/R/insilico_core.r lines 
  509 to 514

UX
* `data` attribute on returned insilico object only has dimnames for rows.
  colnames have been dropped.
* `data` and `indiv.prob` on returned insilico object have different number
  of observations.

DEV API
* using warning() vs cat() for printing warnings
    warning InSilicoVA/R/insilico_core.r line 548
* No way to specify dev external causes. InSilicoVA/R/insilico_core.r line 628
  sets `external.causes <- NULL`
* if you pass `customization.dev=TRUE`, `isNumeric=TRUE`, `external.sep=FALSE`,
  and `datacheck=FALSE` are numerics converted to strings when looking for
  missing InSilicoVA/R/insilico_core.r line 663