# If a spark compatible framework was not already chosen for the primary requirements, consider how the code would change to be executed on a spark engine.

By default this code would all be executed on the driver. 

First few requests (Verion, VersionGroup, Pokedexs) are returning a small amount of data and given there are three sequential requests, not something that Spark could speed up greatly. 

However, when we request data for each Pokemon Species and Pokemon, we could scale this part of the process up.

Rather than make single request, from a list of urls using a for loop, we can utilise Spark to collect data for each pokemon, or at least perform, batches of requests per worker.

This could be acheived by:
* creating a DataFrame, with a column of URLs (`target_url`)
* creating a User Defined Function (UDF) to request and return the json response for the value in `target_url`
* run by running creating a new column `data_response` with `withColumn` executing the request UDF and calling `.show` or another Action that executes the DAG