# DBoT User Manual

User manual for DBoT project

## Grafana setup

1. Go to port 3000 ([http://localhost:3000/](http://10.0.12.65:3000/) or [http://10.0.12.65:3000/](http://localhost:3000/))

2. Login (if asked to) with username: "admin", password: "admin"

3. Go to **"Configuration" -> "Data Sources"**

4. Click **"Add data source"** and search for **"JSON"**

5. In **"url"** put [http://10.0.12.65:3000/<str:user_token>/grafana](http://10.0.12.65:3000/<str:user_token>/grafana) where "<str:user_token>" is the current token you have when you logged in the application

6. Click **"Save & Test"**, a message should appear saying "Data source is working" 

## Create dashboard in grafana (setup is required)

1. Go to **"Create" -> "Dashboard"** and click **"Add an empty panel"**

2. Click in **"Metric"** and choose your metric (example: "1.temperature")

3. Above the graphic, choose your ****time range****

4. On the top right corner click "Apply"

## Add ad hoc filter to a dashboard in grafana (setup is required)

1. Create or edit a dashboard

2. On the top right corner click on the icon to open **dashboard settings**

3. Go to **"Variables"** and click **"Add variable"**

4. In **"Type"** instead of query choose **"Ad hoc filters"**

5. Click **"update"** and go back to the dashboard edit panel

6. On the top left corner click on the **"+" icon** and choose an attribute (ex: "temperature")

7. Choose an **operator** (ex: "=") and type a select **value** (ex: "10")

8. The graphic should now only show values within the conditions of that new ad hoc filter 
added

## API endpoints

### Authentication

**Register** new user **(POST)**: {"name","email","password"}

```bash
/register_user
```

**POST** data example:

```bash
{"name":"test","email":"test@ua.pt","password":"randpassword"}
```

------

**Authenticate** user **(POST)**: {"email","password"}

```bash
/authenticate_user
```

**POST** data example:

```bash
{"email":"test@ua.pt","password":"randpassword"}
```
------

**Logout** user **(GET)** where <str:user_token> is the token given upon login

```bash
/logout_user/<str:user_token>
```
------
### Database 

**Insert** data into user database **(POST)** where **<str:user_token>** is the token given upon login and **<str:sensorid>** is the sensorid where the data will be bound to

```bash
/insert_into_db/<str:user_token>/<str:sensorid>
```
**POST** data example:

```bash
{"sensorid":"0001","temperature":"10","timestamp":"2020-06-01 00:02:10"}
or
[{"sensorid":"0001","temperature":"10","timestamp":"2020-06-01 00:02:10"},
{"sensorid":"0001","temperature":"20","timestamp":"2020-06-02 00:02:10"}]
```
------

**Query** data from user database **(POST)** where **<str:user_token>** is the token given upon login and **<str:sensorid>** is the sensorid where the data will be queried from. If the sensorid given is **"all"** then the query will target all the sensor ids from the user database: {"conditions","attributes","from_ts","to_ts"}

```bash
/query_db/<str:user_token>/<str:sensorid>
```


**POST** data example:
- Multiple **conditions** can be given
- **"attributes"** is the values the query will return
- If **from_ts** is empty, then it will query data from all timestamps


```bash
{"conditions":[["temperature",">","5"]],"attributes":["temperature"],"from_ts":"","to_ts":""}
or
{"conditions":[["temperature",">","5"],["temperature","<=","10"]],"attributes":["temperature"],"from_ts":"2020-05-31","to_ts":"2020-06-02"}
```
------

**Get all attributes** from user database **(GET)** where **<str:user_token>** is the token given upon login

```bash
/get_all_attributes/<str:user_token>
```
------
### Grafana


**Test** connection where **<str:user_token>** is the token given upon login

```bash
/<str:user_token>/grafana
```
------
**Return available metrics when invoked** (Dropdown Metrics when editing a dashboard) where **<str:user_token>** is the token given upon login

```bash
/<str:user_token>/grafana/search
```
------
**Return data based on input** (data showed in graphic based on metric chosen, date range and ad hoc filters) where **<str:user_token>** is the token given upon login

```bash
/<str:user_token>/grafana/query
```
------
Return **annotations** where **<str:user_token>** is the token given upon login

```bash
/<str:user_token>/grafana/annotations
```
------
Return **tag keys** for ad hoc filters where **<str:user_token>** is the token given upon login

```bash
/<str:user_token>/grafana/tag-keys
```
------
Return **tag vaues** for ad hoc filters where **<str:user_token>** is the token given upon login

```bash
/<str:user_token>/grafana/tag-values
```
