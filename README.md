# next-investment-in-realestate

## Pre requisites
Install `miniconda` from [here](https://docs.anaconda.com/miniconda/miniconda-install/)
```sh
conda env create -n realestate python=3.12
conda activate realestate

pip install -r requirements_dev.txt -r requirements.txt
```

## Test the solution
```sh
pytest ./tests
```

## Run the solution
```sh
python -m core.main --debug-mode true
```
