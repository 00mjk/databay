import datetime

from databay import Link
from databay.inlets import HttpInlet
from databay.outlets import MongoOutlet
from databay.planners import APSPlanner

# Create an inlet, outlet and a link.
http_inlet = HttpInlet('https://jsonplaceholder.typicode.com/todos/1')
mongo_outlet = MongoOutlet(database_name='databay', collection='test_collection')
link = Link(http_inlet, mongo_outlet,
            datetime.timedelta(seconds=5), name='http_to_mongo')

# Create a planner, add the link and start scheduling.
planner = APSPlanner()
planner.add_link(link)
planner.start()