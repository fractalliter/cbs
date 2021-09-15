# CBS Electricity and Gas data transformation

## Prerequisites:

* Python 3.7.*
* Pip 20.*

### Installation

If you have Python 3.7 installed on your machine, next you need to create and activate a virtual environemtn and install all the dependencies with following commands:

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

The program designed to get 3 different command line arguments. `--source` which can be utilized for indicating the resources. for example `--source=00372eng,84575ENG` means get data for gas(00372eng) and electricity(84575ENG). Also you can provide only a single source as well. 

No `--source` argument means both gas and electricity.


There is another command argument `--date-range` which can be utilized the same as `--source` but with two different `date` format.

Also you can specify a `--year` command like `--year=2019` to get the data for specified year. No `--year` will fetch data for 2018.

```bash
python cbs.py --source=00372eng,84575ENG --date-range=2021-05-01,1988-12-27 --year=2019
```

In this case gas and electricity data from December 1988 to June 2021 and also for year 2019 will be reterived and transformed.

The output files are `gas.csv` and `electricity.csv` and the transformed data will be:

* Power plant gas consumption in `gas.csv`
* Electricity supply and consumption `electricity.csv`

### Config

There is a `config.json` file which designated for configuring datasets and the columns that need to be fetched. with following schema:
```json
"84575ENG": {
        "title": "electricity",
        "columns": ["Periods", "NetProductionTotal_3", "NetConsumptionCalculated_30"],
        "commodity": {
            "NetProductionTotal_3": "el_prods",
            "NetConsumptionCalculated_30": "el_cons"
        }
    }
```