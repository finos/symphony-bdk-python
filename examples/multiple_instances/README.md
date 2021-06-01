# How to run multiple bot instances?

## Multiple instances reading the same datafeed v2

If multiple instances read the same datafeed (v2) one only will receive an event. If the instance fails to process the
event, it will be re-queued and dispatched to another instance.

The [injector bot](./injector.py) and [reader bot](./reader.py) demo this behavior.

They also make use of Hazelcast to provide a distributed cached to ensure that in the case of an event being slowly
processed it does not get processed by another instance.

To run the example, first install Hazelcast and run `hz start` as shown
[here](https://docs.hazelcast.com/imdg/latest/getting-started).

Then, update the configuration files used in the injector and reader as well as the user IDs used in the injector.
Assuming you ran `poetry install`, run: `poetry run python injector.py` and `poetry run python reader.py` multiples
times in separate shells.
