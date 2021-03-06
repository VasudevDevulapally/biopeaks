import asyncio
from io import StringIO
from timeit import default_timer as timer
import aiohttp
import numpy as np
from wfdb.processing import compare_annotations


class BenchmarkDetectorGUDB:
    """Evaluate an ECG R-peak detector on datasets from the GUDB database.
    """
    channels = {"cs_V2_V1": 0, "einthoven_II": 1, "einthoven_III": 2}
    base_url = "https://berndporr.github.io/ECG-GUDB/experiment_data/subject_"

    def __init__(self, detector, tolerance, sfreq=250, n_runs=100):
        """
        Parameters
        ----------
        detector : function
            A function that takes a 1d array containing a physiological record
            as first positional argument and an integer sampling rate as second
            positional argument. Must return a 1d array containing the detected
            extrema.
        tolerance : int
            Maximum difference in samples that is permitted between the manual
            annotation and the annotation generated by the detector.
        sfreq : int, optional
            The sampling rate of the GUDB records in Hertz, by default 250.
        n_runs : int, optional
            The number of runs used for obtaining the average run time of the
            detector, by default 100.
        """
        self.detector = detector
        self.tolerance = tolerance
        self.sfreq = sfreq
        self.n_runs = n_runs
        self.session = None
        self.queue = None
        self.channel = None
        self.annotation = None
        self.urls = None


    async def score_record(self, record, annotation):
        """Obtain detector performance for an annotated record.

        Parameters
        ----------
        record : 1d array
            The raw physiological record.
        annotation : 1d array
            The manual extrema annotations.

        Returns
        -------
        precision : float
            The detectors precision on the record given the tolerance.
        sensitivity : float
            The detectors sensitivity on the record given the tolerance.

        """
        detector_annotation = self.detector(record, self.sfreq)

        comparitor = compare_annotations(detector_annotation, annotation,
                                         self.tolerance)
        tp = comparitor.tp
        fp = comparitor.fp
        fn = comparitor.fn
        sensitivity = tp / (tp + fn)
        precision = tp / (tp + fp)

        return precision, sensitivity


    async def time_record(self, record):
        """Obtain the average run time of a detector on a record over N runs.

        Parameters
        ----------
        record : 1d array
            The raw physiological record.

        Returns
        -------
        avg_time : int
            The run time of the detector on the record averaged over n_runs. In
            milliseconds.

        """
        start = timer()

        for _ in range(self.n_runs):
            self.detector(record, self.sfreq)

        end = timer()
        avg_time = (end - start) / self.n_runs * 1000

        return avg_time


    async def fetch_record(self, url):
        """Get a record from the GUDB server.

        Fetch the raw physiological data and the corresponding annotation,
        format them, and put them on a queue for further processing.

        Parameters
        ----------
        url : str
            An experiment directory of the GUDB. The URL must end with the
            experiment ID. E.g., "URL/maths". The experiment ID can be one of
            {"maths", "hand_bike", "jogging", "walking", "sitting"}.
        """
        print(f"fetching {url}")
        async with self.session.get(url + "/ECG.tsv") as response:
            if response.status == 200:
                physio = await response.text()
                physio = np.loadtxt(StringIO(physio))
                physio = np.ravel(physio[:, self.channel])
            else:
                physio = None
                # print(f"Couldn't find physio file at {url}")
        async with self.session.get(url + f"/{self.annotation}.tsv") as response:
            if response.status == 200:
                annotation = await response.text()
                annotation = np.loadtxt(StringIO(annotation))
                annotation = np.ravel(annotation)
            else:
                annotation = None
                # print(f"Couldn't find annotation file at {url}")
        await self.queue.put((physio, annotation, url))


    async def benchmark_record(self):
        """Evaluate the performance of the detector on a single record."""
        n = 0
        n_records = len(self.urls)
        sensitivities = []
        precisions = []
        avg_times = []

        while n < n_records:
            # Wait for a record to be added to the queue.
            physio, annotation, url = await self.queue.get()

            skip_record = physio is None
            skip_record = annotation is None

            if skip_record:
                print(f"\nSkipping benchmarking of {url}: missing files.")
                n += 1
                continue

            # Process the record.
            precision, sensitivity = await self.score_record(physio, annotation)
            avg_time = await self.time_record(physio)

            precisions.append(precision)
            sensitivities.append(sensitivity)
            avg_times.append(avg_time)

            n += 1

            print(f"\nResults {url}")
            print("-" * len(url))
            print(f"sensitivity = {sensitivity}")
            print(f"precision = {precision}")
            print(f"average run time over {self.n_runs} runs = {avg_time}")

        print(f"\nAverage results over {len(precisions)} records")
        print("-" * 31)

        mean_avg_time = np.mean(avg_times)
        std_avg_time = np.std(avg_times)
        print(f"average run time over {self.n_runs} runs: mean = {mean_avg_time}, std = {std_avg_time}")

        mean_sensitivity = np.mean(sensitivities)
        std_sensitivity = np.std(sensitivities)
        print(f"sensitivity: mean = {mean_sensitivity}, std = {std_sensitivity}")

        mean_precision = np.mean(precisions)
        std_precision = np.std(precisions)
        print(f"precision: mean = {mean_precision}, std = {std_precision}")


    async def _benchmark_records(self):
        """Evaluate the performance of the detector on a set of records."""
        self.session = aiohttp.ClientSession()
        self.queue = asyncio.Queue()
        fetch_coro = [self.fetch_record(url) for url in self.urls]
        benchmark_coro = self.benchmark_record()

        await asyncio.gather(*fetch_coro, benchmark_coro)
        await self.session.close()


    def benchmark_records(self, experiment, channel="einthoven_II",
                          annotation="annotation_cables"):
        """Wrapper starting the event loop.

        Benchmark a detector on all available records from all 25 subjects for a
        given combination of experiment, channel, and annotation.

        Parameters
        ----------
        experiment : str
            The name of the experiment to be benchmarked. Can be one of
            {"sitting", "maths", "walking", "hand_bike", "jogging"}.
        channel : str, optional
            The ECG channel to be benchmarked. Can be one of {"cs_V2_V1",
            "einthoven_II", "einthoven_III"}, by default "einthoven_II".
        annotation : str, optional
            The annotation file used for benchmarking. Can be one of
            {"annotation_cs", "annotation_cables"}, by default
            "annotation_cables".
        """
        if experiment not in ["sitting", "maths", "walking", "hand_bike", "jogging"]:
            raise ValueError(f"{experiment} is not a valid experiment.")
        if channel not in self.channels.keys():
            raise ValueError(f"{channel} is not a valid channel")
        if annotation not in ["annotation_cs", "annotation_cables"]:
            raise ValueError(f"{annotation} is not a valid annotation")
        self.channel = self.channels[channel]
        self.annotation = annotation
        self.urls = [f"{self.base_url}{str(i).zfill(2)}/{experiment}/" for i in range(25)]
        asyncio.run(self._benchmark_records())
