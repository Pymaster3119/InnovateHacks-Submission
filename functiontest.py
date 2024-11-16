import gpt_interactor
import datetime
import pytz
def gettime(timezone):
    return f"{datetime.datetime.now(pytz.timezone(timezone)).timetuple().tm_hour}:{datetime.datetime.now(pytz.timezone(timezone)).timetuple().tm_min}:{datetime.datetime.now(pytz.timezone(timezone)).timetuple().tm_sec}"

def getdate(timezone):
    return f"{datetime.datetime.now(pytz.timezone(timezone)).timetuple().tm_mon}/{datetime.datetime.now(pytz.timezone(timezone)).timetuple().tm_mday}/{datetime.datetime.now(pytz.timezone(timezone)).timetuple().tm_year}"

gettimefunction = gpt_interactor.function(
    "gettime", 
    "This gets the time of day in a given timezone", 
    [
        {"name":"timezone", 
         "type":"string", 
         "description":"the timezone you want to call"}
    ], 
    gettime, 
    "time")

print(gpt_interactor.run_query(
    "gpt-4o-mini", 
    "You are a helpful assistant", 
    "Find me the current time in California", None, None, [gettimefunction], False)
)

