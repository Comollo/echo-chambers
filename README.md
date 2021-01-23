# echo-chambers
MSc in Data Science at University of Milan - Bicocca

The project concerns the development of a pipeline for controversy reduction on Social Media.

## Folders:

```
docs: it contains the pdf of the thesis
betweenness: it contains values for the computed bewteenness
effective_size: it contains values for the computed effective_size
jaccard_coefficient: it contains values for the computed jaccard coeff
preferential_attachment: it contains values for the computed preferential attachment
resource_allocation: it contains values for the computed resource allocation
adamic_adar: it contains values for the computed adamic adar
notebook: it contains useful notebook to analyse results and graphs
analysis_paper: it contains just the controversial graphs used for further analysis
data: it contains the data used to carry out the analysis for the thesis
community: it contains the communities created using FluidC
result_standard: it contains the standard results of the analysis 
result_hybrid: it contains the hybrid results of the analysis 
src: it contains all the code
```

## Structure of the code - src

```
common: there are defined some commons utility functions
communitiy: there are defined the classes to implement the graph partitioning algorithms
controversy: there are defined the classes to implement the controversy measures
link prediction: there are defined the classes to implement the link prediction algorithms
main.py: it is the main code
```

## How to run the code:

```
run "python main.py --help" for usage
```