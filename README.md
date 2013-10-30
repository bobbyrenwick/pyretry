# Pyretry

[![Build Status](https://travis-ci.org/bobbyrenwick/pyretry.png)](https://travis-ci.org/bobbyrenwick/pyretry)

Are you tired of rewriting the same code for catching exceptions and then retrying the original code? pyretry allows you to separate your retry logic from your business logic by allowing you to specify which exceptions you would like to retry on, the number of times to retry, how long to timeout between retries and provides a hook on each retry for you to log or do whatever you will with that information.

Enough chat. Here's the code

```python
@retry(pymongo.errors.AutoReconnect, num_retries=5)
def insert_into_collection(collection, document)
    return collection.insert(document)
```

Or if you want to catch multiple exceptions:

```python
@retry((requests.exceptions.ConnectionError, requests.exceptions.Timeout), num_retries=5)
def fetch_entity_at_url(url)
    return requests.get(url)
```

If you specify `num_retries=2`, then a total of 3 attempts will be made.

You can specify a timeout as a float or a function that gets invoked with the number of the attempt that has
been made (0 indexed):

```python
retry_with_constant_timeout = retry(pymongo.errors.AutoReconnect, timeout=0.5)


@retry_with_constant_timeout
def some_function:
    ...


retry_with_exponential_backoff = retry(
    pymongo.errors.AutoReconnect,
    timeout=lambda num_attempts: pow(2, num_attempts) / 10
)

@retry_with_exponential_backoff
def some_other_function:
    ...

```

You can also specify a hook function that gets passed the following arguments
`exception, num_attempts, calculated_timeout`

```python
def print_on_retry(exception, num_attempts, calculated_timeout):
    print exception, num_attempts, calculated_timeout

retry_with_logging = retry(pymongo.errors.AutoReconnect, hook=print_on_retry)
```
