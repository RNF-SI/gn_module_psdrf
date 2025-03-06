
# Stub for easypackages
# This provides a simpler version of the libraries function from easypackages package

libraries <- function(...) {
  pkgs <- c(...)
  
  # Loop through packages and load them
  loaded <- sapply(pkgs, function(pkg) {
    if (!require(pkg, character.only = TRUE)) {
      message(paste("Package", pkg, "not available."))
      return(FALSE)
    } else {
      return(TRUE)
    }
  })
  
  return(loaded)
}
