library('InSilicoVA')

# Windows compatibility, replace backslash with forward slash in passed path
REPO_DIR <- gsub("\\\\", "/", commandArgs(trailingOnly=TRUE)[1])

members <- c("InsilicoVA", "causetext", "condprob", "condprobnum", "csmf.diag",
             "extract.prob", "get.indiv", "indivplot", "insilico",
             "insilico.fit", "insilico.train", "RandomVA1", "RandomVA2",
             "stackplot", "summary.insilico", "updateIndiv")

outdir <- file.path(REPO_DIR, "docs", "_static", "r_help")

for (member in members) {
  outfile <- paste0(sub("[.]", "_", member, perl=T), ".html")
  capture.output(tools:::Rd2HTML(utils:::.getHelpFile(help(member))),
                 file=file.path(outdir, outfile))
}

file.copy(file.path(R.home("doc"), "html", "R.css"), file.path(outdir, "R.css"))
