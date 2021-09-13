# CBS Electricity and Gas data transformation

## Prerequisites:

* Python 3.7
* Pip 20.*

### Installation

If you have Python 3.7 installed on your machine, next you need to install all the dependencies with following command:

```bash
# Create virtual environment(venv)
python3 -m venv env

# Activate the venv
source env/bin/activate

#install dependencies
pip install -r requirements.txt
```
### Test

After installation finished you can test the application with following command:

```bash
python -m unittest
```

### Run

The program designed to get 2 different command line arguments. `--source` which can be utilized for indicating the resources. for example `--source=gas,electricity` means get data for gas and electricity. Also you can provide only a single source as well. 

No `--source` argument means both gas and electricity.


There is another command argument `--date-range` which can be utilized the same as `--source` but with two different `date` format.

```bash
python cbs_elec_gas.py --source=gas,electricity --date-range=2021-05-01,1988-12-27
```

In this case gas and electricity data from December 1988 to June 2021 will be reterived and transformed.

The output files are `gas.csv` and `electricity.csv` and the transformed data will be:

* Power plant gas consumption in `gas.csv`
* Electricity supply and consumption `electricity.csv`