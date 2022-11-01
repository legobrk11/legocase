## Imagine you had to build a system in the cloud that would continiously deliver updates to the investor with updates about Pokémon. Draw an architecture for exposing new changes to the existing Pokémon to the investor

```mermaid
graph TB;
    PokeAPI ---> LambdaFunction
    LambdaFunction ---> |"1) Periodic HEAD request for each<br/>Pokemon endpoint"|PokeAPI
    LambdaFunction --->  |"2) Lambda validates header etag<br/>against cached latest version"| DB[(CacheDB)]
    DB[(CacheDB)] ---> LambdaFunction
    LambdaFunction ---> |"3) If cached etag != requested etag, <br/>fetch new data for that Pokemon <br/> and push data to queue"| Queue
    Queue --->|"4) Database updated"| PokemonDB
    PokemonDB --->|"4) Notification Data updated"| Slack/Email/Teams
    PokemonDB --->|"5) User can access updated data"| User

```
### Notes:
* Architecture depends on a serverless (e.g. Lambda) function that periodically checks for updates. 
* As no date modified is included API (appears to be infrequently updated), etags contained in the API response headers are exploited
* If PokeAPI was internal resource, possible it could push an update to message queue and avoid periodic "HEAD" on requests and reduce update latency.
* SQL DB chosen to store data, but csv/parquet file on S3 could be used. Updated data could also be pushed via Slack/Email but likely stakeholder would want whole dataset.
