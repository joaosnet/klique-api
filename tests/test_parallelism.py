import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def cpu_bound_task(count):
    """A CPU intensive task that just loops and calculates."""
    n = 0
    while n < count:
        n += 1
    return n


def run_threads(num_threads, task_size):
    """Run the CPU task across multiple threads and measure time."""
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(cpu_bound_task, task_size)
            for _ in range(num_threads)
        ]
        for f in futures:
            f.result()

    end_time = time.time()
    return end_time - start_time


def run_processes(num_processes, task_size):
    """Run the CPU task across multiple processes and measure time."""
    start_time = time.time()

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = [
            executor.submit(cpu_bound_task, task_size)
            for _ in range(num_processes)
        ]
        for f in futures:
            f.result()

    end_time = time.time()
    return end_time - start_time


def test_threading_vs_multiprocessing():
    """Verify that multiprocessing bypasses the GIL for true parallelism."""
    task_size = 50_000_000

    print('\nRunning Parallelism Performance Test (Std Python 3.14 + GIL)...')

    # Run sequential (1 worker doing 2 tasks)
    print('Running sequential (1 thread, 2 tasks)...')
    seq_time = run_threads(1, task_size * 2)
    print(f'Sequential time: {seq_time:.3f} seconds')

    # Run Threads
    print('\nRunning parallel THREADS (2 threads, 1 task each)...')
    thread_time = run_threads(2, task_size)
    print(f'Thread time (GIL blocked): {thread_time:.3f} seconds')

    # Run Processes
    print('\nRunning parallel PROCESSES (2 processes, 1 task each)...')
    process_time = run_processes(2, task_size)
    print(f'Process time (GIL bypassed): {process_time:.3f} seconds')

    thr_speedup = seq_time / thread_time
    print(f'\nThreading Speedup: {thr_speedup:.2f}x (Expect ~1.0x)')
    proc_speedup = seq_time / process_time
    print(f'MultiProc Speedup: {proc_speedup:.2f}x (Expect >1.5x)')

    # Assert true parallelism in ProcessPool
    expected_speedup = 1.2
    assert proc_speedup > expected_speedup, (
        'Failed parallel benefit check for multiprocessing.'
    )


if __name__ == '__main__':
    test_threading_vs_multiprocessing()
