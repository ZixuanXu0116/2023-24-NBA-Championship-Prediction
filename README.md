# 2023-24-NBA-Championship-Prediction

## A. Data Scraping and Cleaning
 
***Source:*** We scraped the NBA normal and advanced data of players and teams in playoffs and regular seasons from https://www.basketball-reference.com/


***Execution method:*** To execute the code and load the data to your database, you should:
* Create a Google Cloud Platform (GCP) account and set up a project.
* Enable the necessary APIs for your project, such as the PostgreSQL API if you're using PostgreSQL.
* Create a database on GCP.
* After the GCP database has been set up completely, please follow the commands and instructions below.

```python  

git clone git@github.com:ZixuanXu0116/2023-24-NBA-Championship-Prediction.git

cd 2023-24-NBA-Championship-Prediction

pip install -r requirements.txt 

```

* Then create a .env file in the same format as demo.env by changing the attributes inside like passwords, host, database name to the ones of your own database.


```python
python3 code/data_scraping/get_NBA_data.py

```

