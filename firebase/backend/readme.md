## How To

#### Create CRUD Object
For "Create \ Read \ ~~Update~~ \ ~~Delete~~" actions you should first create crud object: 
```python
from google.cloud import firestore
from firebase_crud import BaseCrud

conn = firestore.Client(project='openbus')
siri_rides_crud = BaseCrud(connection=conn, collection_name='siri_rides')
```

#### Add New Document to DB
```python
from google.cloud import firestore
from firebase_crud import BaseCrud

conn = firestore.Client(project='openbus')
siri_rides_crud = BaseCrud(connection=conn, collection_name='siri_rides')
doc = dict(foo='bar')
siri_rides_crud.create(content=doc)
```

#### Get Document from DB
```python
from google.cloud import firestore
from firebase_crud import BaseCrud

conn = firestore.Client(project='openbus')
siri_rides_crud = BaseCrud(connection=conn, collection_name='siri_rides')
doc = dict(foo='bar')
siri_rides_crud.create(content=doc, doc_id='baz')
result = siri_rides_crud.read(doc_id='baz')
```

#### Create SiriRide Document and Add it to DB
```python
from datetime import datetime
from google.cloud import firestore
from firebase_crud import BaseCrud
from firebase_documents import SiriRide, SiriPoint, Point

conn = firestore.Client(project='openbus')
siri_rides_crud = BaseCrud(connection=conn, collection_name='siri_rides')
doc = SiriRide(route_id=1001, agency_id=5, bus_id='23456', planned_start_datetime=datetime.fromtimestamp(1),
               route_short_name='None', stop_point_ref=(1.1, 2.2), trip_id_to_date=57434, 
               points=[SiriPoint(point=Point(1.1, 2.2), rec_dt=datetime.fromtimestamp(1),
               pred_dt=datetime.fromtimestamp(1))], foo=4)

siri_rides_crud.create(content=doc.to_firebase_dict())

```
