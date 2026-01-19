#%%
from confluent_kafka import Producer
import pyarrow.parquet as pq
import time
import pandas as pd

topic_name = "nyc_taxicab_data"
conf = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(conf)

print(producer.list_topics().topics)
print("-----------------------------")

# trips = pq.read_table('yellow_tripdata_2022-03.parquet')
trips = trips.to_pandas()

trips = trips[['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'PULocationID', 'DOLocationID', 'trip_distance', 'fare_amount']]

bronx = [3, 18, 20, 31, 32, 46, 47, 51, 58, 59, 60, 69, 78, 81, 94, 119, 126, 136, 147, 159, 167, 168, 169, 174, 182, 183, 184, 185, 199, 200, 208, 212, 213, 220, 235, 240, 241, 242, 247, 248, 250, 254, 259]
trips = trips[trips.iloc[:, 2].isin(bronx) & trips.iloc[:, 3].isin(bronx)]
trips = trips[trips['trip_distance'] > 0.1]
trips = trips[trips['fare_amount'] > 2.5]
trips['tpep_pickup_datetime'] = pd.to_datetime(trips['tpep_pickup_datetime'], format='%Y-%m-%d %H:%M:%S')
trips['tpep_dropoff_datetime'] = pd.to_datetime(trips['tpep_dropoff_datetime'], format='%Y-%m-%d %H:%M:%S')


print(trips.shape[0])
#%%
counter = 0
for index, row in trips.iterrows():
    counter += 1

    row = row[['trip_distance', 'PULocationID', 'DOLocationID', 'fare_amount']]

    row = row.to_json()
    
    message = str(row).encode('utf-8')

    producer.produce(topic_name, value=message)
    producer.flush()

    print(counter)
    print("Message sent to Kafka: {}".format(message))


    time.sleep(0.25)

print('all done')

